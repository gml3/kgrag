"""
Entity — 实体模型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Entity:
    """知识图谱实体的数据模型。

    通过 LLM 从文本块中抽取的命名实体，经过去重与描述合并后存储。
    实体是知识图谱的核心节点，也是 Local Search 的检索锚点。
    """

    id: str
    """实体唯一标识"""

    title: str = ""
    """实体名称（如人名、组织名、地名等）"""

    type: str = ""
    """实体类型（PERSON, ORGANIZATION, LOCATION, EVENT 等）"""

    description: str = ""
    """实体描述（经过摘要合并后的文本）"""

    text_unit_ids: list[str] = field(default_factory=list)
    """来源文本块 ID 列表"""

    rank: float = 0.0
    """实体重要度（基于图的 degree 计算）"""

    community_ids: list[str] = field(default_factory=list)
    """所属社区 ID 列表"""

    description_embedding: Optional[list[float]] = None
    """实体描述的向量表示（`title:description` 的 Embedding）"""

    @property
    def embedding_text(self) -> str:
        """用于生成 Embedding 的文本：`title:description`"""
        return f"{self.title}:{self.description}" if self.description else self.title
