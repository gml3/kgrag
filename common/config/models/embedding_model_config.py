"""
Embedding 模型配置
"""

from dataclasses import dataclass, field


@dataclass
class EmbeddingModelConfig:
    """Embedding 模型的调用配置"""

    api_base: str = "http://192.168.10.82:7200/v2/embeddings"
    """API 地址"""

    headers: dict = field(default_factory=lambda: {
        "accept": "application/json",
        "Content-Type": "application/json",
    })
