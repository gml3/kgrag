# config — 配置管理

> 统一管理 KGRAG 系统的全局配置参数

## 核心配置项

| 配置组 | 配置项 | 说明 |
|--------|--------|------|
| **LLM** | `model_name`, `api_base`, `api_key`, `temperature`, `max_tokens` | Chat 模型参数 |
| **Embedding** | `model_name`, `api_base`, `vector_dim` | Embedding 模型参数 |
| **Chunking** | `chunk_size`, `chunk_overlap` | 文档分块参数 |
| **Storage** | `parquet_dir`, `milvus_uri`, `milvus_collection` | 存储配置 |
| **Search** | `max_context_tokens`, `top_k_entities`, `community_prop`, `text_unit_prop` | 搜索参数 |

## 预期文件

```
config/
├── __init__.py
├── README.md
├── settings.py        # 配置数据类定义
└── defaults.py        # 默认配置值
```
