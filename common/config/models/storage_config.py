from dataclasses import dataclass, field


@dataclass
class StorageConfig:
    """数据存储配置"""

    parquet_dir: str = "./data/output"
    """Parquet 文件存储目录"""

    milvus_uri: str = "http://localhost:19530"
    """Milvus 连接地址"""

    milvus_db_name: str = "kgrag"
    """Milvus 数据库名"""

    entity_collection: str = "entity_description"
    """实体描述向量 collection 名"""

    text_unit_collection: str = "text_unit_text"
    """文本块向量 collection 名（可选）"""