# models — 数据模型定义

> 知识图谱核心数据结构

## 数据模型

| 模型 | 关键字段 | 来源 |
|------|---------|------|
| **Document** | id, title, raw_content | 原始文档 |
| **TextUnit** | id, text, n_tokens, document_ids, entity_ids | 文档分块 |
| **Entity** | id, title, type, description, rank, community_ids | 实体抽取 |
| **Relationship** | id, source, target, description, weight, rank | 关系抽取 |
| **Community** | id, level, entity_ids, relationship_ids, parent, children | 社区发现 |
| **CommunityReport** | id, community_id, title, summary, full_content, rank | 社区报告 |
| **Covariate** | id, subject_id, covariate_type, description, status | 协变量（可选） |

## 预期文件

```
models/
├── __init__.py
├── README.md
├── document.py
├── text_unit.py
├── entity.py
├── relationship.py
├── community.py
└── covariate.py
```
