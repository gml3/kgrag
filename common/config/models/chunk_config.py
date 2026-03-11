from dataclasses import dataclass, field


@dataclass
class ChunkingConfig:
    """文档分块配置"""

    chunk_size: int = 1200
    """每个文本块的 token 数"""

    chunk_overlap: int = 100
    """相邻文本块的重叠 token 数"""