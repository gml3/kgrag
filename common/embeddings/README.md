# embeddings — Embedding 模型封装

> 文本向量化接口封装

## 核心接口

```
BaseEmbedding (ABC)
├── embed(text) → list[float]
├── embed_batch(texts) → list[list[float]]
└── dimension → int
```

## Embedding 目标

| 内容 | 用途 | 优先级 |
|------|------|--------|
| 实体描述 `title:description` | Local Search | ✅ 必须 |
| 文本块 `text` | Basic Search | 可选 |
| 社区报告 `full_content` | DRIFT Search | 可选 |

## 预期文件

```
embeddings/
├── __init__.py
├── README.md
├── base.py        # Embedding 抽象基类
└── bge_m3.py      # bge-m3 模型实现
```
