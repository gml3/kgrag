"""
TextUnit — 文本块模型
"""

from dataclasses import dataclass, field


@dataclass
class TextUnit:
    """文本块的数据模型。

    文档按固定 token 数分块后的产物，是实体/关系抽取的基本输入单元，
    也是搜索时提供原文证据的核心来源。
    """

    id: str
    """文本块唯一标识"""

    text: str = ""
    """文本内容"""

    n_tokens: int = 0
    """文本的 token 数量"""

    document_ids: list[str] = field(default_factory=list)
    """来源文档 ID 列表"""

    entity_ids: list[str] = field(default_factory=list)
    """该文本块中包含的实体 ID"""

    relationship_ids: list[str] = field(default_factory=list)
    """该文本块中包含的关系 ID"""
