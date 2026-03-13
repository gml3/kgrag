import logging
from typing import Any, List, Optional
import pandas as pd

from chat.search.base import BaseSearch

from common.config.models.local_search_config import LocalSearchConfig
from common.storage.milvus_storage import MilvusStorage
from common.storage.mysql_storage import MysqlStorage

from common.llm.chat_model import LitellmChatModel

from chat.search.local_search.context_builder import ContextBuilder


logger = logging.getLogger(__name__)

class LocalSearch(BaseSearch):
    """
    Local Search 实现。
    直接将 User Query 发送至 Embedding 接口将其向量化，
    利用 MilvusStorage 在向量库检索 Top-K 实体，提取其 id。
    然后去 MySQL 存储中提取该实体的社区报告、关系、文本库组装混合上下文交由 LLM 回答。
    """

    def __init__(
        self,
        llm: LitellmChatModel,
        config: LocalSearchConfig,
        **kwargs: Any
    ):
        super().__init__(llm, **kwargs)
        self.config = config
        
        # 初始化存储服务
        self.milvus_storage = MilvusStorage(self.config.milvus)
        self.mysql_storage = MysqlStorage(self.config.mysql)
        
        # 从 MySQL 将知识图谱全量加载至内存 Pandas (以供 ContextBuilder 抽取使用)
        entities_df = self.mysql_storage.read_df("entities")
        relationships_df = self.mysql_storage.read_df("relationships")
        text_units_df = self.mysql_storage.read_df("text_units")
        community_reports_df = self.mysql_storage.read_df("community_reports")
        
        self.context_builder = ContextBuilder(
            entities_df, relationships_df, text_units_df, community_reports_df
        )
        
        self.system_prompt = self.config.system_prompt
        self.max_tokens = self.config.max_tokens
        self.top_k = self.config.top_k

    def search(self, query: str, **kwargs: Any) -> Any:
        from common.embeddings.client import convert_text_to_vec
        
        # 1. 向量化 query
        try:
            dense_vectors, _ = convert_text_to_vec([query], self.config.embedding_model)
            query_vector = dense_vectors[0]
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: {e}")
            return "对不起，当前系统发生内部异常：嵌入模型服务调用失败。"

        # 2. 检索 Milvus 实体
        try:
            search_res = self.milvus_storage.search(
                collection_name=self.config.collection_name,
                data=[query_vector],
                limit=self.top_k,
                output_fields=["id", "entity_title"]
            )
        except Exception as e:
            logger.error(f"Failed to search in Milvus: {e}")
            return "对不起，当前系统发生内部异常：Milvus 向量库检索失败。"

        if not search_res or not search_res[0]:
            logger.warning(f"No entities matched for query: {query}")
            return "未能在这个知识图谱中检索到相关信息以回答此问题。"
            
        # 从命中结果提取实体的唯一标识符及其名字
        matched_entity_ids_or_titles = [hit["id"] for hit in search_res[0]]

        # 3. 构建混合上下文
        context_data = self.context_builder.build_context(
            matched_entities=matched_entity_ids_or_titles,
            max_tokens=self.max_tokens,
            community_prop=kwargs.get("community_prop", 0.25),
            text_unit_prop=kwargs.get("text_unit_prop", 0.50)
        )

        # 4. 拼装 prompt
        prompt = self.system_prompt.format(context_data=context_data)
        
        # 5. LLM 生成
        history = kwargs.get("history", [])
        response = self.llm.chat(prompt=query, history=[{"role": "system", "content": prompt}] + history)
        
        return response

    async def asearch(self, query: str, **kwargs: Any) -> Any:
        # 同步转异步可以用 asyncio.to_thread 或者如果在 LLM SDK 中有真正的 async chat 则调用
        import asyncio
        return await asyncio.to_thread(self.search, query, **kwargs)
