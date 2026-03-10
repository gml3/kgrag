# chat/prompts — 搜索阶段 Prompt 模板

> 检索问答过程中 LLM 调用所需的 Prompt 模板

## Prompt 模板

| 模板 | 用途 | 关键变量 |
|------|------|---------|
| `local_search_system.txt` | Local Search 系统提示词 | `{context_data}`, `{response_type}` |
| `global_search_map.txt` | Global Search Map 阶段 | `{context_data}`, `{query}` |
| `global_search_reduce.txt` | Global Search Reduce 阶段 | `{report_data}`, `{query}` |

### 引用规范
- 要求 LLM 在回答中标注数据来源
- 格式: `[Data: Entities (id); Sources (id)]`
