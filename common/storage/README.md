# storage — 数据存储

> 管理知识图谱的持久化：MySQL（结构化）+ Milvus（向量）

## 结构化存储（MySQL）

通过 `MysqlStorage` 类管理，利用 SQLAlchemy 和 Pandas 实现高效的数据读写。数据模型在保存时会自动序列化为 JSON 字符串。

| 数据表 | 说明 | 对应模型 |
|--------|------|----------|
| `documents` | 文档元信息 | `Document` |
| `text_units` | 文本块 | `TextUnit` |
| `entities` | 实体信息 | `Entity` |
| `relationships` | 实体间关系 | `Relationship` |
| `communities` | Leiden 聚类社区 | `Community` |
| `community_reports` | 社区摘要报告 | `CommunityReport` |

## 向量存储（Milvus）

通过 `MilvusStorage` 类封装，提供向量检索服务。

| Collection | 内容 | 场景 |
|------------|------|------|
| `entity_description` | 实体描述向量 | Local Search 核心检索项 |
| `text_unit_text` | 文本块向量 | 基础 RAG 检索（可选） |

## 模块结构

```
storage/
├── __init__.py
├── README.md
├── mysql_storage.py     # MySQL 读写服务（基于 SQLAlchemy + Pandas）
└── milvus_storage.py    # Milvus 向量搜索服务封装
```
