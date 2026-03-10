"""
Community & CommunityReport — 社区模型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Community:
    """社区的数据模型。

    通过 Leiden 算法在实体-关系图上聚类发现的层级社区结构。
    社区用于 Global Search 和 DRIFT Search 中的宏观背景信息。
    """

    id: str
    """社区唯一标识"""

    level: int = 0
    """社区层级（0 为最底层，数字越大层级越高）"""

    entity_ids: list[str] = field(default_factory=list)
    """社区内包含的实体 ID 列表"""

    relationship_ids: list[str] = field(default_factory=list)
    """社区内包含的关系 ID 列表"""

    parent: Optional[str] = None
    """父社区 ID（上层社区）"""

    children: list[str] = field(default_factory=list)
    """子社区 ID 列表"""


@dataclass
class CommunityReport:
    """社区报告的数据模型。

    由 LLM 为每个社区生成的摘要报告，描述社区内的核心实体、
    关系和主题。用于搜索阶段提供宏观背景上下文。
    """

    id: str
    """报告唯一标识"""

    community_id: str = ""
    """所属社区 ID"""

    title: str = ""
    """报告标题"""

    summary: str = ""
    """摘要"""

    full_content: str = ""
    """完整内容"""

    rank: float = 0.0
    """重要度（用于搜索时的排序和上下文分配）"""

    full_content_embedding: Optional[list[float]] = None
    """报告完整内容的向量表示（DRIFT Search 使用）"""
