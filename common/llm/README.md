# llm — LLM 接口封装

> 封装 Chat LLM 调用接口

## 核心接口

```
BaseLLM (ABC)
├── chat(messages) → str
├── chat_with_json(messages) → dict
└── count_tokens(text) → int
```

## 预期文件

```
llm/
├── __init__.py
├── README.md
├── base.py                # LLM 抽象基类
├── openai_compatible.py   # OpenAI 兼容 API（适配 Qwen3 等本地模型）
└── utils.py               # Token 计数、重试逻辑
```

## 配置参数

| 参数 | 说明 |
|------|------|
| `model_name` | 模型名称（Qwen3-30B-A3B-Instruct-2507） |
| `api_base` | API 地址（本地部署） |
| `api_key` | API Key |
| `temperature` | 温度参数 |
| `max_tokens` | 最大 token 数 |
