"""milvus 配置"""
from dataclasses import dataclass


@dataclass
class MilvusConfig:
    """Milvus 配置"""

    host: str = "192.168.10.82"
    """Milvus 主机"""

    port: int = 19530
    """Milvus 端口"""

    db_name: str = "knowledge_gyz"
    """Milvus 数据库名"""

    collection_name: str = "kgrag"
    """Collection 名称"""