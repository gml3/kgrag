from dataclasses import dataclass


@dataclass
class DescriptionSummarizerConfig:
    """描述合并去重配置"""

    concat_threshold: int = 2
    """实体、关系的描述数量低于此阈值时，直接拼接而不调用 LLM"""