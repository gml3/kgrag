# kg_construct — 知识图谱构建

> 索引 Pipeline：从原始文档构建知识图谱的完整流水线

## 职责

将原始文档转化为结构化知识图谱，包含以下步骤：

1. **文档加载** — 读取原始文档（txt/pdf/csv/json）
2. **文档分块** — 按固定 token 数切分为 text_units
3. **实体抽取** — LLM 从文本块中提取命名实体
4. **关系抽取** — LLM 提取实体间的关系
5. **描述合并** — 同名实体/关系的描述进行摘要合并
6. **社区发现** — Leiden 算法发现层级社区结构
7. **社区报告** — LLM 为每个社区生成摘要报告
8. **向量生成** — 为实体描述等内容生成 Embedding

## 数据流

```
原始文档
  → [document_loader] → Document 列表
  → [chunker] → TextUnit 列表
  → [entity_extractor] → Entity 列表（含描述合并）
  → [relationship_extractor] → Relationship 列表（含描述合并）
  → [community_detector] → Community 列表
  → [report_generator] → CommunityReport 列表
  → [embedding_generator] → 各类向量
  → [pipeline] → 写入 Storage（Parquet + Milvus）
```

## 预期文件

```
kg_construct/
├── __init__.py
├── README.md
├── pipeline.py               # 索引流水线编排
├── document_loader.py        # 文档加载器（多格式支持）
├── chunker.py                # 文档分块器
├── entity_extractor.py       # LLM 实体抽取
├── relationship_extractor.py # LLM 关系抽取
├── description_summarizer.py # 描述摘要合并
├── community_detector.py     # Leiden 社区发现
├── report_generator.py       # LLM 社区报告生成
├── embedding_generator.py    # Embedding 向量生成
└── prompts/                  # 构建阶段 Prompt 模板
    ├── __init__.py
    ├── README.md
    ├── entity_extraction.txt
    ├── relationship_extraction.txt
    ├── summarize_descriptions.txt
    └── community_report.txt
```

## 关键参数（来自 common.config）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `chunk_size` | 300 | 分块 token 数 |
| `chunk_overlap` | 100 | 分块重叠 token 数 |
| `entity_types` | PERSON, ORG, LOCATION, EVENT | 实体类型列表 |
| `community_algorithm` | leiden | 社区检测算法 |
| `embedding_targets` | entity_description | 需要生成向量的内容 |

## 依赖关系

- 依赖 `common.models` — 数据模型
- 依赖 `common.llm` — LLM 调用
- 依赖 `common.embeddings` — Embedding 生成
- 依赖 `common.storage` — 数据持久化
- 依赖 `common.config` — 配置参数
