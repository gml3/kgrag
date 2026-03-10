# KGRAG — 知识图谱增强检索生成

> 基于 Knowledge Graph 的 RAG 系统，参考 Microsoft GraphRAG 架构设计

## 总体架构

```
原始文档 → [索引Pipeline] → 知识图谱 + 向量库 → [搜索引擎] → LLM → 回答
```

---

## 1. 知识图谱构建（Indexing Pipeline）

### 1.1 文档加载与分块

- **输入**: 原始文档（txt/pdf/csv/json 等）
- **分块策略**: 按固定 token 数切分（如 chunk_size=300, overlap=100）
- **输出**: `text_units`（文本块列表）
- **关键字段**: `id, text, n_tokens, document_ids`
- **待决策**:
  - [ ] 分块大小和重叠度的最优值
  - [ ] 是否支持按段落/标题语义分块

### 1.2 实体抽取

- **方法**: LLM 从每个文本块中提取命名实体
- **Prompt 设计**: 指定要提取的实体类型（PERSON, ORGANIZATION, LOCATION, EVENT 等）
- **去重与合并**: 相同实体名的描述通过 LLM 或规则进行摘要合并（`summarize_descriptions`）
- **输出**: `entities` 列表
- **关键字段**: `id, title, type, description, text_unit_ids, rank(degree)`
- **待决策**:
  - [ ] 实体类型是固定枚举还是开放式
  - [ ] 实体消歧策略（同名不同义如何处理）
  - [ ] 是否使用 NER 工具辅助 LLM 抽取以降低成本

### 1.3 关系抽取

- **方法**: LLM 从文本块中提取实体间的关系
- **输出**: `relationships` 列表
- **关键字段**: `id, source, target, description, weight, text_unit_ids, rank(combined_degree)`
- **描述合并**: 相同 source-target 对的关系描述做摘要合并
- **待决策**:
  - [ ] 关系是否有类型分类（如 WORKS_FOR, MARRIED_TO）还是纯自由文本
  - [ ] 关系 weight 的计算方式（出现频次、LLM 打分等）

### 1.4 社区发现与社区报告

- **社区聚类**: 对实体-关系图执行 Leiden 算法，发现层级社区结构
- **社区报告**: LLM 为每个社区生成摘要报告，描述社区内的核心实体、关系和主题
- **输出**:
  - `communities`: `id, level, entity_ids, relationship_ids, parent, children`
  - `community_reports`: `id, community_id, title, summary, full_content, rank`
- **待决策**:
  - [ ] 是否需要多层级社区（level 0/1/2）
  - [ ] 社区 rank 的计算方式
  - [ ] 社区报告是否需要 embedding（DRIFT Search 需要）

### 1.5 协变量/声明（可选）

- **说明**: 从文本中提取实体相关的声明（claims），如时间、状态等结构化信息
- **输出**: `covariates`: `id, subject_id, covariate_type, description, status, start_date, end_date`
- **待决策**:
  - [ ] 是否需要此功能（增加 LLM 调用成本）

### 1.6 Embedding 生成

- **对以下内容生成向量**:
  - ✅ `entity_description`: 实体 `title:description` 的 embedding → **Local Search 核心依赖**
  - 可选: `text_unit_text` → Basic Search 使用
  - 可选: `community_report_full_content` → DRIFT Search 使用
  - 可选: `relationship_description`
- **Embedding 模型选择**:
  - embedding: beg-m3
  - [ ] 向量维度（1536/768/384）

---

## 2. 数据存储

### 2.1 结构化存储（Parquet / 数据库）

存储知识图谱的所有结构化数据：

| 数据表 | 说明 | 关键用途 |
|--------|------|----------|
| `documents` | 原始文档元信息 | 溯源 |
| `text_units` | 文本块 | 搜索上下文（原文证据） |
| `entities` | 实体 | 搜索锚点 |
| `relationships` | 关系 | 关联扩展 |
| `communities` | 社区层级 | 社区定位 |
| `community_reports` | 社区摘要 | 宏观背景 |
| `covariates` | 声明/协变量 | 结构化事实 |

- **选型**: **Parquet 文件**
  - 存储全量结构化数据（实体、关系、社区、社区报告、文本块、协变量）
  - 搜索时加载到内存，通过 id 关联构建上下文
  - 轻量无依赖，适合单机部署

### 2.2 向量存储

存储 Embedding 向量，用于语义相似搜索：

| 向量表 | 内容 | 字段 |
|--------|------|------|
| `entity_description` | 实体描述向量 | id, text, vector, attributes |
| `text_unit_text`（可选） | 文本块向量 | id, text, vector, attributes |

- **选型**: **Milvus**（高性能分布式向量数据库）
  - 索引类型：IVF_FLAT（精度优先）或 HNSW（速度优先）
  - 支持增量插入和删除
  - 支持标量过滤 + 向量检索混合查询
  - 部署方式：Milvus Lite（本地开发）/ Milvus Standalone（单机）/ Milvus Cluster（生产）

### 2.3 图谱可视化

- **目的**: 直观展示实体-关系网络、社区结构
- **选型**: **Pyvis**（交互式网页可视化）
  - 基于 vis.js，生成可拖拽、缩放、悬停查看详情的 HTML 页面
  - NetworkX 图可直接转为 Pyvis 渲染
  - 无需后端服务，生成静态 HTML 即可分享
- **可视化内容**:
  - 实体-关系图（节点=实体，边=关系）
  - 社区高亮（不同社区用不同颜色）
  - 节点大小按 degree/rank 缩放

---

## 3. 搜索与问答

### 3.1 搜索模式设计

| 模式 | 核心思想 | 数据依赖 | LLM 调用次数 | 适用场景 |
|------|---------|---------|-------------|---------|
| **Basic Search** | 传统 RAG 文本块检索 | text_units 向量 | 1 次 | 简单事实查询 |
| **Local Search** | 知识图谱局部混合检索 | entity 向量 + 全部表 | 1 次 | 特定实体相关问题 |
| **Global Search** | 社区报告 Map-Reduce | community_reports | N+1 次 | 全局概括性问题 |
| **DRIFT Search** | 迭代深化探索 | community 向量 + entity 向量 | 多轮 | 复杂深入问题 |

- **待决策**:
  - [ ] 初期实现哪些模式（建议先做 Local Search）
  - [ ] 是否支持多模式自动路由（根据问题类型自动选择）

### 3.2 Local Search 流程（核心实现）

```
用户 Query
  → 1. Embedding 模型将 query 转为向量
  → 2. 向量库中检索 top-K 相关实体
  → 3. 构建混合上下文:
       ├── 社区报告 (25%) — 匹配实体所属社区的摘要
       ├── 实体/关系表 (25%) — 结构化关联信息
       └── 文本块 (50%) — 原始文本证据
  → 4. 拼装 System Prompt + 混合上下文
  → 5. Chat 模型生成回答
```

**关键参数**:
- `max_context_tokens`: 上下文窗口大小（默认 12000）
- `top_k_mapped_entities`: 检索实体数量（默认 10）
- `community_prop / text_unit_prop`: 上下文比例分配

### 3.3 Prompt 工程

- **System Prompt 模板**:
  - 角色定义: "你是一个基于知识图谱数据回答问题的助手"
  - 数据表格占位: `{context_data}` — 社区报告 + 实体/关系表 + 文本块
  - 响应格式: `{response_type}` — 如 "multiple paragraphs"
  - 引用规范: 要求标注数据来源 `[Data: Entities (id); Sources (id)]`
- **待决策**:
  - [ ] Prompt 是否支持自定义/可配置
  - [ ] 是否支持多语言 Prompt

### 3.4 对话历史

- 支持多轮对话，将历史问答拼入上下文
- 历史 query 也参与实体映射（扩大检索范围）
- **待决策**:
  - [ ] 最大历史轮数
  - [ ] 历史信息的 token 预算

---

## 4. 技术选型清单

| 组件 | 候选方案 | 备注 |
|------|---------|------|
| **Chat LLM** | Qwen3-30B-A3B-Instruct-2507 | 实体抽取 + 问答生成 |
| **Embedding** | beg-m3 | 向量生成 |
| **向量库** | ✅ Milvus | 语义检索 |
| **结构化存储** | Parquet | 知识图谱数据 |
| **图数据库**（可选） | NetworkX | 图遍历查询 |
| **社区检测** | Leiden (graspologic) | 图聚类 |
| **Web 框架** | FastAPI | API/演示界面 |

---

## 5. 开发路线图

### Phase 1: MVP（基础可用）
- [ ] 文档加载与分块
- [ ] LLM 实体/关系抽取
- [ ] 向量生成与存储（Milvus）
- [ ] Local Search 实现
- [ ] 基本 CLI/API 接口

### Phase 2: 增强（完善功能）
- [ ] 社区检测与社区报告
- [ ] Global Search 实现
- [ ] 图谱可视化
- [ ] 增量更新（不重建整个图谱）
- [ ] 多文档类型支持（PDF、Word）

### Phase 3: 生产化（部署优化）
- [ ] DRIFT Search 实现
- [ ] 自动搜索模式路由
- [ ] Web UI 界面
- [ ] 性能优化（并发抽取、批量 embedding）
- [ ] 监控与日志

---

## 附录: 与 GraphRAG 的区别

| 维度 | GraphRAG | KGRAG（本项目） |
|------|---------|----------------|
| 定位 | 研究框架 | 轻量级实用工具 |
| 复杂度 | 高（10+ workflow） | 精简核心流程 |
| 模型依赖 | 主要 OpenAI | 支持本地模型 |
| 存储 | Parquet + LanceDB | 灵活可选 |
| 图谱可视化 | 无内置 | 内置支持 |
