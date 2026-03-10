# chat — 检索问答

> 基于知识图谱的检索增强问答系统

## 职责

- 接收用户 query，执行语义检索
- 使用向量库检索相关实体/文本块
- 构建混合上下文（社区报告 + 实体关系 + 文本块）
- 调用 LLM 基于上下文生成回答
- 管理多轮对话历史
- 提供 FastAPI 接口服务

## 搜索模式

| 模式 | 核心思想 | 数据依赖 | LLM 调用 | 适用场景 | 优先级 |
|------|---------|---------|----------|---------|--------|
| **Local Search** | 知识图谱局部混合检索 | entity 向量 + 全部表 | 1 次 | 特定实体相关问题 | Phase 1 ✅ |
| **Basic Search** | 传统 RAG 文本块检索 | text_units 向量 | 1 次 | 简单事实查询 | Phase 1 |
| **Global Search** | 社区报告 Map-Reduce | community_reports | N+1 次 | 全局概括性问题 | Phase 2 |
| **DRIFT Search** | 迭代深化探索 | community + entity 向量 | 多轮 | 复杂深入问题 | Phase 3 |

## Local Search 核心流程

```
用户 Query
  → 1. Embedding 模型将 query 转为向量
  → 2. Milvus 中检索 top-K 相关实体
  → 3. 构建混合上下文:
       ├── 社区报告 (25%) — 匹配实体所属社区的摘要
       ├── 实体/关系表 (25%) — 结构化关联信息
       └── 文本块 (50%) — 原始文本证据
  → 4. 拼装 System Prompt + 混合上下文
  → 5. Chat 模型生成回答
```

## 预期文件

```
chat/
├── __init__.py
├── README.md
├── context_builder.py     # 混合上下文构建器
├── conversation.py        # 对话历史管理
├── search/                # 搜索引擎
│   ├── __init__.py
│   ├── README.md
│   ├── base.py            # 搜索引擎抽象基类
│   ├── local_search.py    # Local Search 实现
│   ├── global_search.py   # Global Search（Phase 2）
│   ├── basic_search.py    # Basic Search
│   └── drift_search.py    # DRIFT Search（Phase 3）
├── prompts/               # 搜索阶段 Prompt 模板
│   ├── __init__.py
│   ├── README.md
│   ├── local_search_system.txt
│   ├── global_search_map.txt
│   └── global_search_reduce.txt
└── api/                   # FastAPI 接口服务
    ├── __init__.py
    ├── README.md
    ├── app.py
    ├── schemas.py
    └── routes/
        └── __init__.py
```

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_context_tokens` | 12000 | 上下文窗口大小 |
| `top_k_mapped_entities` | 10 | 检索实体数量 |
| `community_prop` | 0.25 | 社区报告上下文占比 |
| `text_unit_prop` | 0.50 | 文本块上下文占比 |

## 依赖关系

- 依赖 `common.models` — 数据模型
- 依赖 `common.storage` — 数据加载
- 依赖 `common.llm` — Chat 模型调用
- 依赖 `common.embeddings` — Query 向量化
- 依赖 `common.config` — 搜索参数
