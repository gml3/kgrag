import logging
from typing import Any, List, Optional
import pandas as pd

from chat.search.base import BaseSearch
from chat.context_builder import ContextBuilder
from common.llm.chat_model import LitellmChatModel

logger = logging.getLogger(__name__)

class LocalSearch(BaseSearch):
    """
    Local Search 实现。
    通过将 User Query 向量化，在向量库检索 Top-K 实体，
    然后去知识图谱存储中提取该实体的社区报告、关系、文本库组装混合上下文交由 LLM 回答。
    """

    def __init__(
        self,
        llm: LitellmChatModel,
        context_builder: ContextBuilder,
        vector_search_func: Any,  # 可以是一个 callable: func(query_text, top_k) -> List[str] 返回 Entity Title 列表
        system_prompt: Optional[str] = None,
        max_tokens: int = 12000,
        **kwargs: Any
    ):
        super().__init__(llm, **kwargs)
        self.context_builder = context_builder
        self.vector_search = vector_search_func
        
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
        # 1. 向量化 query 并检索实体
        matched_entities = self.vector_search(query, top_k)
        if not matched_entities:
            logger.warning(f"No entities matched for query: {query}")
            return "未能在这个知识图谱中检索到相关信息以回答此问题。"

        # 2. 构建混合上下文
        context_data = self.context_builder.build_context(
            matched_entities=matched_entities,
            max_tokens=self.max_tokens,
            community_prop=kwargs.get("community_prop", 0.25),
            text_unit_prop=kwargs.get("text_unit_prop", 0.50)
        )

        # 3. 拼装 prompt
        prompt = self.system_prompt.format(context_data=context_data)
        
        # 4. LLM 生成
        history = kwargs.get("history", [])
        response = self.llm.chat(prompt=query, history=[{"role": "system", "content": prompt}] + history)
        
        return response

    async def asearch(self, query: str, **kwargs: Any) -> Any:
        # 同步转异步可以用 asyncio.to_thread 或者如果在 LLM SDK 中有真正的 async chat 则调用
        import asyncio
        return await asyncio.to_thread(self.search, query, **kwargs)
