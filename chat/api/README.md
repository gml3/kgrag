# chat/api — FastAPI 接口服务

> 提供 RESTful API 接口

## API 端点设计

### 搜索问答

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/search` | 执行搜索（指定搜索模式） |
| `POST` | `/api/chat` | 对话式问答（支持历史） |

### 索引管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/index/run` | 触发索引 Pipeline |
| `GET` | `/api/index/status` | 查询索引状态 |

### 数据查看

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/entities` | 查看实体列表 |
| `GET` | `/api/graph` | 获取图谱可视化 HTML |

## 预期文件

```
api/
├── __init__.py
├── README.md
├── app.py               # FastAPI 应用入口
├── schemas.py           # 请求/响应模型
└── routes/
    └── __init__.py
```
