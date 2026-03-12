from dataclasses import dataclass, field


@dataclass
class DocumentLoaderConfig:
    """文档加载配置"""
    
    input_dir: str = field(default="./data")
    """输入目录"""
    
    supported_extensions: list[str] = field(default_factory=lambda: [".txt", ".csv", ".json"])
    """支持的文件扩展名"""
    