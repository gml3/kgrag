from dataclasses import dataclass, field


@dataclass
class EntityExtractorConfig:
    """实体抽取配置"""
    
    entity_types: list[str] = field(default_factory=lambda: ["人", "组织", "位置", "事件"])
    """实体类型列表"""
    
    tuple_delimiter: str = "<|>"
    """元组分隔符"""
    
    record_delimiter: str = "##"
    """记录分隔符"""
    
    completion_delimiter: str = "<|COMPLETE|>"
    """完成分隔符"""
    