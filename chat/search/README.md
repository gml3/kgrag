# chat/search — 搜索引擎

> 提供多种搜索模式的具体实现

## 预期文件

| 文件 | 说明 | 优先级 |
|------|------|--------|
| `base.py` | 搜索引擎抽象基类 | Phase 1 |
| `local_search.py` | 知识图谱局部混合检索 | Phase 1 ✅ |
| `basic_search.py` | 传统 RAG 文本块检索 | Phase 1 |
| `global_search.py` | 社区报告 Map-Reduce | Phase 2 |
| `drift_search.py` | 迭代深化探索 | Phase 3 |
