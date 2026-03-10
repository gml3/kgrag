"""
Chat LLM 模型配置
"""

from dataclasses import dataclass


@dataclass
class ChatModelConfig:
    """Chat LLM 的调用配置。

    适配 OpenAI 兼容 API（本地部署的 Qwen3 等模型）。
    """

    model: str = "openai/Qwen3-30B-A3B-Instruct-2507"
    """模型名称（对应 litellm 的 model 参数）"""

    api_base: str = "http://61.172.168.152:11025/v1"
    """API 地址（本地部署）"""

    api_key: str = "sk-XvxxUxzpsmv9Y9gAyfEgGtidngY6eN3khhvCv4vPcWBr1FkS"
    """API Key（本地部署可为空）"""

    temperature: float = 0.0
    """温度参数（0 表示确定性输出，适合抽取任务）"""

    top_p: float = 1.0
    """核采样参数"""

    n: int = 1
    """每次请求生成的回答数量"""

    max_tokens: int = 8000
    """单次生成最大 token 数"""

    max_retries: int = 3
    """API 调用最大重试次数"""

    request_timeout: float = 60.0
    """请求超时时间（秒）"""

    concurrent_requests: int = 10
    """并发请求数"""
