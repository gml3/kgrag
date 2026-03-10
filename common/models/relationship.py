"""
Relationship — 关系模型
"""

from dataclasses import dataclass, field


@dataclass
class Relationship:
    """实体间关系的数据模型。

    通过 LLM 从文本块中抽取的实体间关系，相同 source-target 对
    的关系描述会经过摘要合并。关系是知识图谱的边。
    """

    id: str
    """关系唯一标识"""

    source: str = ""
    """源实体 ID"""

    target: str = ""
    """目标实体 ID"""

    description: str = ""
    """关系描述（经过摘要合并后的文本）"""

    weight: float = 1.0
    """关系权重（基于出现频次或 LLM 打分）"""

    text_unit_ids: list[str] = field(default_factory=list)
    """来源文本块 ID 列表"""

    rank: float = 0.0
    """重要度（combined_degree：source + target 的 degree 之和）"""
