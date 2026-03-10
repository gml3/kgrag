# """
# defaults.py — 默认配置实例

# 提供开箱即用的默认配置，适用于本地开发和测试。
# """

# from dataclasses import dataclass, field

# from common.config.models.chat_model_config import ChatModelConfig
# from common.config.models.embedding_model_config import EmbeddingModelConfig
# from common.config.models.chunk_config import ChunkingConfig
# from common.config.models.storage_config import StorageConfig
# from common.config.models.search_config import SearchConfig


# @dataclass
# class KGRAGConfig:
#     """KGRAG 系统全局配置。

#     聚合所有子配置项，提供统一的配置入口。

#     Usage::

#         config = KGRAGConfig()
#         config.llm.model = "my-model"
#         config.search.top_k_mapped_entities = 20
#     """

#     llm: ChatModelConfig = field(default_factory=ChatModelConfig)
#     """Chat LLM 配置"""

#     embedding: EmbeddingModelConfig = field(default_factory=EmbeddingModelConfig)
#     """Embedding 模型配置"""

#     chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
#     """文档分块配置"""

#     storage: StorageConfig = field(default_factory=StorageConfig)
#     """数据存储配置"""

#     search: SearchConfig = field(default_factory=SearchConfig)
#     """搜索参数配置"""

#     input_dir: str = "./data/input"
#     """原始文档输入目录"""

#     output_dir: str = "./data/output"
#     """产出数据输出目录"""