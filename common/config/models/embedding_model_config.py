"""
Embedding 模型配置
"""

from dataclasses import dataclass


@dataclass
class EmbeddingModelConfig:
    """Embedding 模型的调用配置。

    默认使用 bge-m3 模型。
    """

    model_name: str = "bge-m3"
    """模型名称"""

    api_base: str = "http://localhost:8000/v1"
    """API 地址"""

    api_key: str = "EMPTY"
    """API Key"""

    vector_dim: int = 1024
    """向量维度"""

    batch_size: int = 32
    """批量 Embedding 时的批大小"""

    max_retries: int = 3
    """最大重试次数"""
