# kg_construct/prompts — 构建阶段 Prompt 模板

> 知识图谱构建过程中 LLM 调用所需的 Prompt 模板

## Prompt 模板

| 模板 | 用途 | 关键变量 |
|------|------|---------|
| `entity_extraction.txt` | 从文本块提取实体 | `{input_text}`, `{entity_types}` |
| `relationship_extraction.txt` | 从文本块提取关系 | `{input_text}`, `{entity_types}` |
| `summarize_descriptions.txt` | 合并同名实体/关系描述 | `{descriptions}` |
| `community_report.txt` | 为社区生成摘要报告 | `{community_entities}`, `{community_relationships}` |
