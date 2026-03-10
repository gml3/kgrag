# common — 共享基础模块

> `kg_construct` 和 `chat` 两阶段共享的基础设施

## 子模块

| 子模块 | 职责 | 说明 |
|--------|------|------|
| `config/` | 配置管理 | 全局配置（LLM、Embedding、存储、搜索等参数） |
| `models/` | 数据模型 | Entity, Relationship, Community, TextUnit 等 |
| `llm/` | LLM 接口封装 | Qwen3 等模型的 API 调用 |
| `embeddings/` | Embedding 封装 | bge-m3 向量模型 |
| `storage/` | 数据存储 | Parquet 读写 + Milvus 向量存储 |
| `visualization/` | 图谱可视化 | Pyvis 交互式 HTML 生成 |
| `utils/` | 工具函数 | ID 生成、日志、Token 计数等 |

## 依赖方向

```
kg_construct ──→ common ←── chat
```

`common` 不依赖 `kg_construct` 或 `chat`，确保两阶段可以独立使用。
