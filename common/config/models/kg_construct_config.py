"""构建知识图谱所用配置"""

from dataclasses import dataclass, field

# 模型配置
from common.config.models.chat_model_config import ChatModelConfig
from common.config.models.embedding_model_config import EmbeddingModelConfig
from common.config.models.tokenizer_config import TokenizerConfig

# 文件读取配置
from common.config.models.document_loader_config import DocumentLoaderConfig

# 数据存储配置
from common.config.models.milvus_config import MilvusConfig
from common.config.models.mysql_config import MysqlConfig

# 工作流配置
from common.config.models.chunk_config import ChunkingConfig
from common.config.models.entity_extractor_config import EntityExtractorConfig
from common.config.models.description_summarizer_config import DescriptionSummarizerConfig
from common.config.models.community_config import CommunityConfig
from common.config.models.report_config import ReportConfig
from common.config.models.storage_config import StorageConfig




@dataclass
class KGConstructConfig:
    """构建知识图谱配置"""

    # 标准索引所需配置

    chat_model: ChatModelConfig = field(default_factory=ChatModelConfig)
    """chatModel 配置"""

    embedding_model: EmbeddingModelConfig = field(default_factory=EmbeddingModelConfig)
    """embeddingModel 配置"""

    tokenizer: TokenizerConfig = field(default_factory=TokenizerConfig)
    """tokenizer 配置"""

    documentloader: DocumentLoaderConfig = field(default_factory=DocumentLoaderConfig)
    """文档配置"""

    milvus: MilvusConfig = field(default_factory=MilvusConfig)
    """Milvus 配置"""

    mysql: MysqlConfig = field(default_factory=MysqlConfig)
    """MySQL 配置"""

    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    """分块配置"""

    entity_extractor: EntityExtractorConfig = field(default_factory=EntityExtractorConfig)
    """实体抽取配置"""  

    description_summarizer: DescriptionSummarizerConfig = field(default_factory=DescriptionSummarizerConfig)
    """描述摘要配置"""

    community_detector: CommunityConfig = field(default_factory=CommunityConfig)
    """社区发现配置"""