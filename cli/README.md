# cli — 命令行接口

> KGRAG 命令行入口

## 命令设计

```bash
# 索引构建
kgrag index --input ./data/input --output ./data/output

# 搜索
kgrag search --mode local --query "你的问题"

# 交互式对话
kgrag chat --mode local

# 图谱可视化
kgrag visualize --output ./data/output/graph.html
```

## 预期文件

```
cli/
├── __init__.py
├── README.md
└── main.py       # CLI 入口
```
