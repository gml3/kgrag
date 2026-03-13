# Local Search — 局部搜索模块

> 基于知识图谱局部结构的混合检索算法。

Local Search 是 KGRAG 的核心检索模式，旨在通过“实体锚点”召回知识图谱中紧密关联的局部信息，解决特定实体相关的复杂问答（如“江门公积金的提取流程是什么？”）。

## 核心工作流

1. **向量召回**：将用户查询（Query）向量化，从 Milvus 向量库中检索 Top-K 个最相关的“实体”。
2. **知识关联**：利用 search 返回的实体 ID，去 MySQL 数据库中捞取该实体周围的“一跳”知识。
3. **上下文构建**：通过 `ContextBuilder` 进行多维度数据融合。
4. **生成回答**：将组装好的混合上下文输入给 LLM 生成最终答案。

---

## 关键组件

### 1. LocalSearch (`local_search.py`)
整个搜索流程的控制器。
- **解耦设计**：初始化时接受 `LocalSearchConfig`，不直接持有数据库连接，而是通过 `MilvusStorage` 和 `MysqlStorage` 服务存取数据。
- **内存优化**：为了提高搜索速度，初始化时会将 MySQL 中的核心图谱表（entities, relationships 等）一次性加载到内存 Pandas DataFrame 中，避免高频 IO。

### 2. ContextBuilder (`context_builder.py`)
`ContextBuilder` 是搜索系统的“主厨”，负责将 Milvus 检索到的实体 ID 转化为 LLM 能够理解的混合上下文。其核心逻辑遵循 **“多维关联 -> 按比例分配 -> 贪婪填充”** 的算法：

#### A. 核心算法流程
1.  **Token 预算切分**：
    - 根据输入总额 `max_tokens`（默认 12000），按预设比例划分为三个独立池。
    - **社区池 (25%)**：提供全局视野。
    - **原文池 (50%)**：提供底层证据。
    - **图结构池 (25%)**：提供实体链接。
2.  **多维并行召回**：
    - **社区摘要提取**：通过实体查找其所属的 `community_ids`。从 `community_reports` 中按 `rank`（如有）降序排列提取摘要。如果一个实体属于多个社区，其权重会叠加。
    - **图谱局部探测**：
        - 提取实体自身的描述（`description`）。
        - 提取“一跳”关系：筛选 `source` 或 `target` 在匹配列表中的所有 `relationships` 记录。
    - **原文块溯源**：查阅实体的 `text_unit_ids`，从 `text_units` 表中反查出原始文本片段。
3.  **序列化与截断**：
    - 对每块数据执行贪婪循环，使用 `len / 1.5` 快速估算 Token。
    - 一旦该维度的预算耗尽，立即停止添加新记录，确保不会导致 LLM 窗口溢出。

#### B. 数据呈现格式
为了让 LLM 更好地结构化理解，`ContextBuilder` 将数据格式化为以下文本结构：
- **实体**：`Entity: {name} ({type}) Desc: {description}`
- **关系**：`Rel: {source} -> {target} Desc: {description}`
- **社区**：`Title: {title} Summary: {summary}`
- **原文**：`Text [{id}]: {text_content}`

#### C. 截断策略细节
- **简易估算**：使用 `len / 1.5` 作为 Token 计算常数，这是一种平衡中英文混排计算速度与准确度的启发式方案。
- **占比优先级**：在“实体与关系”池中，实体描述默认最多占用该池预算的一半，余下空间留给关系描述，以保证图谱的“连通性信息”不被单一实体的长篇大论淹没。

---

## 数据依赖

| 数据表 | 用途 |
|--------|------|
| `entities` | 提供映射关系及描述 |
| `relationships` | 提供实体间的关联路径 |
| `text_units` | 提供原文事实证据 |
| `community_reports` | 提供全局层面的总结 |
| `Milvus Collection` | 提供基于描述向量的相似度匹配 |
