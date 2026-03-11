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

## 工作流与数据结构详解（附全流程示例）

> 💡 **贯穿示例假设**：
> 输入一篇介绍性短文：“*小明是一家名为 AI-Tech 的科技公司高管。2023年他代表公司去北京参加了人工智能峰会。*”

整个知识构建流水线分为 8 个核心阶段，以下是每个阶段处理逻辑及其产出数据的详细说明与示例展示：

### 1. 文档加载 (document_loader)
此阶段负责对源文件进行解析。
- **输入**: 原始文件内容。
- **输出**: `Document` 列表。
- **数据字段与示例**:
  - `id`: `"doc_001"`
  - `content`: `"小明是一家名为 AI-Tech 的科技公司高管。2023年他代表公司去北京参加了人工智能峰会。"`
  - `metadata`: `{"source": "news.txt", "author": "admin"}`

### 2. 文档分块 (chunker)
将整篇文稿切分为固定 Token 的片段，以便 LLM 处理和搜索溯源证据。
- **输入**: `Document` 列表
- **输出**: `TextUnit` 列表 (`text_units.parquet`)
- **数据字段与示例**:
  - `id`: `"chunk_001"`
  - `text`: `"小明是一家名为 AI-Tech 的科技公司高管。2023年他代表公司去北京参加了人工智能峰会。"`
  - `n_tokens`: `32`
  - `document_ids`: `["doc_001"]`
  - `entity_ids`: `["ent_xiaoming", "ent_aitech", "ent_beijing"]` *(注: 抽取完填补)*
  - `relationship_ids`: `["rel_x_a", "rel_x_b"]` *(注: 抽取完填补)*

### 3. 实体抽取 (entity_extractor)
基于 Prompt 驱使 LLM 从每个 `TextUnit` 中抽取出相关类型（人、组织、地点等）的命名实体。此过程输出“源头草稿”实体。
- **输入**: `TextUnit` 列表
- **输出**: 暂存的 **Raw Entity** 和 **Raw Relationship**
  - *Raw Entity 示例*: 
    - `{"title": "小明", "type": "PERSON", "desc": "AI-Tech 的高管", "source_id": "chunk_001"}`
    - `{"title": "AI-Tech", "type": "ORG", "desc": "一家科技公司", "source_id": "chunk_001"}`
  - *Raw Relationship 示例*: 
    - `{"source": "小明", "target": "AI-Tech", "desc": "小明是 AI-Tech 的高管"}`

### 4. 描述合并与去重 (description_summarizer)
将名称相同的特征与关系的背景描述聚合并用 LLM 汇总成一份。
- **输入**: Raw Entities, Raw Relationships
- **输出**: 最终定稿的单节点 `Entity` 及其关联边 `Relationship`
- **Entity 数据字段与示例** (`entities.parquet`):
  - `id`: `"ent_xiaoming"`
  - `title`: `"小明"`
  - `type`: `"PERSON"`
  - `description`: `"AI-Tech 公司的科技高管，曾作为代表出席过 2023 年人工智能峰会。"`
  - `text_unit_ids`: `["chunk_001"]`
  - `community_ids`: `["comm_0"]` *(注: 聚类后填补)*
  - `rank`: `1.5`
- **Relationship 数据字段与示例** (`relationships.parquet`):
  - `id`: `"rel_x_a"`
  - `source`: `"ent_xiaoming"`
  - `target`: `"ent_aitech"`
  - `description`: `"小明在 AI-Tech 公司担任高管职位。"`
  - `weight`: `1.0`
  - `rank`: `2.0`

### 5. 社区发现 (community_detector)
在 Entity 与 Relationship 构建的拓扑图上发现并划分多级子群结构，高频互动实体聚在底层级社区。
- **输入**: `Entity`, `Relationship`
- **输出**: `Community` 列表 (`communities.parquet`)
- **数据字段与示例**:
  - `id`: `"comm_0"`
  - `level`: `0` 
  - `parent`: `"comm_high_1"` 
  - `children`: `[]` 
  - `entity_ids`: `["ent_xiaoming", "ent_aitech"]` 
  - `relationship_ids`: `["rel_x_a"]`

### 6. 社区报告生成 (report_generator)
LLM 生成针对各社区的一份全面描述，总结社区实体为何集结等宏观内容。
- **输入**: `Community` 及其下属实体和关系边
- **输出**: `CommunityReport` (`community_reports.parquet`)
- **数据字段与示例**:
  - `id`: `"rep_0"`
  - `community_id`: `"comm_0"` 
  - `title`: `"AI-Tech 高管层与峰会活动"`
  - `summary`: `"该社区主要围绕科技公司 AI-Tech 及其高管小明的人工智能峰会行程展开。"`
  - `full_content`: `"详细报告：AI-Tech 是一家科技企业，小明作为其高管，在 2023 年扮演了……(省略)"`
  - `rank`: `0.85`

### 7. 向量化入库 (embedding_generator & pipeline)
为实体标题及生成描述进行向量嵌入，结果存入 Milvus。其他表归档以便上下文检索。
- **存储介质与示例**:
  - **Milvus** `entity_description` 集合。包含 `id="ent_xiaoming"`, `text="小明:AI-Tech 公司的科技..."`, `entity_title="小明"`, `type="PERSON"`, `vector=[0.012, -0.043, ...]`
  - **Parquet**: 之前各个步骤中的 `TextUnit`, `Entity`, `Relationship`, `Community` 都作为 Parquet 持久化在磁盘。

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
