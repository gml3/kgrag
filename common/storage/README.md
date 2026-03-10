# storage — 数据存储

> 管理知识图谱的持久化：Parquet（结构化）+ Milvus（向量）

## 结构化存储（Parquet）

| 数据表 | 说明 |
|--------|------|
| `documents.parquet` | 文档元信息 |
| `text_units.parquet` | 文本块 |
| `entities.parquet` | 实体 |
| `relationships.parquet` | 关系 |
| `communities.parquet` | 社区 |
| `community_reports.parquet` | 社区报告 |

## 向量存储（Milvus）

| Collection | 内容 |
|------------|------|
| `entity_description` | 实体描述向量 |
| `text_unit_text` | 文本块向量（可选） |

## 预期文件

```
storage/
├── __init__.py
├── README.md
├── base.py              # 存储抽象基类
├── parquet_store.py     # Parquet 读写
├── milvus_store.py      # Milvus 向量存储
└── data_loader.py       # 搜索时数据加载器
```
