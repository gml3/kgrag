# Prompt 模板

> 知识图谱构建过程中 LLM 调用所需的 Prompt 模板

## Prompt 模板

| 模板 | 用途 | 关键变量 |
|------|------|---------|
| `entity_extraction.txt` | 从文本块提取实体 | `{input_text}`, `{entity_types}` |
| `relationship_extraction.txt` | 从文本块提取关系 | `{input_text}`, `{entity_types}` |
| `summarize_descriptions.txt` | 合并同名实体/关系描述 | `{descriptions}` |
| `community_report.txt` | 为社区生成摘要报告 | `{community_entities}`, `{community_relationships}` |


> chat过程中 LLM 调用所需的 Prompt 模板

## Prompt 模板

| 模板 | 用途 | 关键变量 |
|------|------|---------|
| `local_search_system.txt` | Local Search 系统提示词 | `{context_data}`, `{response_type}` |
| `global_search_map.txt` | Global Search Map 阶段 | `{context_data}`, `{query}` |
| `global_search_reduce.txt` | Global Search Reduce 阶段 | `{report_data}`, `{query}` |

### 引用规范
- 要求 LLM 在回答中标注数据来源
- 格式: `[Data: Entities (id); Sources (id)]`