from dataclasses import dataclass

@dataclass
class TokenizerConfig:
    """Tokenizer 配置"""
    
    encoding_name:  str = "cl100k_base"
    """编码"""