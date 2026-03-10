from dataclasses import dataclass, field


@dataclass
class SearchConfig:
    """搜索参数配置"""

    max_context_tokens: int = 12000
    """上下文窗口最大 token 数"""

    top_k_mapped_entities: int = 10
    """检索实体数量"""

    top_k_relationships: int = 10
    """每个实体关联的关系数量上限"""

    top_k_text_units: int = 20
    """检索文本块数量上限"""

    community_prop: float = 0.25
    """社区报告在上下文中的占比"""

    entity_relationship_prop: float = 0.25
    """实体/关系在上下文中的占比"""

    text_unit_prop: float = 0.50
    """文本块在上下文中的占比"""

    conversation_history_max_turns: int = 5
    """对话历史最大轮数"""