from dataclasses import dataclass, field
from typing import Optional, List

# 模型配置
from common.config.models.chat_model_config import ChatModelConfig
from common.config.models.embedding_model_config import EmbeddingModelConfig

# 数据存储配置
from common.config.models.milvus_config import MilvusConfig
from common.config.models.mysql_config import MysqlConfig

# prompt
from common.prompts.search.local_search_system import LOCAL_SEARCH_SYSTEM_PROMPT

@dataclass
class LocalSearchConfig:
    """
    Local search configuration.
    """

    chat_model: ChatModelConfig = field(default_factory=ChatModelConfig)
    """chatModel 配置"""

    embedding_model: EmbeddingModelConfig = field(default_factory=EmbeddingModelConfig)
    """embeddingModel 配置"""

    milvus: MilvusConfig = field(default_factory=MilvusConfig)
    """Milvus 配置"""

    mysql: MysqlConfig = field(default_factory=MysqlConfig)
    """MySQL 配置"""

    collection_name: str = "entity_description"
    """Milvus 集合名称"""

    max_tokens: int = 12000
    """最大 token 数"""

    system_prompt: str = LOCAL_SEARCH_SYSTEM_PROMPT
    """系统提示词"""

    top_k: int = 10
    """Top-K 实体数"""