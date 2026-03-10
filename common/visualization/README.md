# visualization — 图谱可视化

> Pyvis 交互式知识图谱可视化

## 可视化映射

| 元素 | 视觉 | 说明 |
|------|------|------|
| 节点 | 圆形 | 实体，大小按 rank 缩放 |
| 节点颜色 | 社区 | 不同社区不同颜色 |
| 边 | 连接线 | 关系，粗细按 weight |
| 悬停 | 弹窗 | 显示 description |

## 预期文件

```
visualization/
├── __init__.py
├── README.md
├── graph_builder.py     # NetworkX 图构建
└── renderer.py          # Pyvis 渲染器
```
