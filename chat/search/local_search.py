import logging
from typing import Any, List, Optional
import pandas as pd

from chat.search.base import BaseSearch
from chat.context_builder import ContextBuilder
from common.llm.chat_model import LitellmChatModel
from pymilvus import MilvusClient

logger = logging.getLogger(__name__)

class LocalSearch(BaseSearch):
    """
    Local Search 实现。
    直接将 User Query 发送至 Embedding 接口将其向量化，
    利用内置的 MilvusClient 在向量库检索 Top-K 实体，提取其 id。
    然后去知识图谱存储中提取该实体的社区报告、关系、文本库组装混合上下文交由 LLM 回答。
    """

    def __init__(
        self,
        llm: LitellmChatModel,
        context_builder: ContextBuilder,
        embedding_config: "EmbeddingModelConfig",
        milvus_config: "MilvusConfig",
        collection_name: str = "entity_description",
        system_prompt: Optional[str] = None,
        max_tokens: int = 12000,
        **kwargs: Any
    ):
        super().__init__(llm, **kwargs)
        self.context_builder = context_builder
        self.embedding_config = embedding_config
        self.milvus_config = milvus_config
        self.collection_name = collection_name
        
        # 建立 Milvus 长连接
        self.milvus_client = MilvusClient(
            uri=f"http://{self.milvus_config.host}:{self.milvus_config.port}",
            db_name=self.milvus_config.db_name
        )
        
        if system_prompt is None:
            prompt_path = pd.io.common.Path(__file__).parent.parent / "prompts" / "local_search_system.txt"
            if prompt_path.exists():
                with open(prompt_path, "r", encoding="utf-8") as f:
                    self.system_prompt = f.read()
            else:
                self.system_prompt = (
                    "你是一个基于知识图谱数据回答问题的助手。\n"
                    "请基于以下提供的数据表上下文回答问题。在可能的情况下，提供数据引用（例如：[Data: Entities (id); Sources (id)]）。\n\n"
                    "=== 上下文数据 ===\n"
                    "{context_data}\n"
                    "================\n"
                )
        else:
            self.system_prompt = system_prompt
            
        self.max_tokens = max_tokens

    def search(self, query: str, top_k: int = 10, **kwargs: Any) -> Any:
        from common.embeddings.client import convert_text_to_vec
        
        # 1. 向量化 query
        try:
            dense_vectors, _ = convert_text_to_vec([query], self.embedding_config)
            query_vector = dense_vectors[0]
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: {e}")
            return "对不起，当前系统发生内部异常：嵌入模型服务调用失败。"

        # 2. 检索 Milvus 实体
        try:
            search_res = self.milvus_client.search(
                collection_name=self.collection_name,
                data=[query_vector],
                limit=top_k,
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
