# AI Agent 管理系统 API 文档

## 项目概述
本系统是基于 FastAPI 构建的 AI Agent 管理平台，提供 Agent 的创建、存储、加载和交互功能。系统使用 SQLite 进行数据存储，支持通过 API Key 进行身份验证，并提供完整的 RESTful API 接口。



## 技术栈
- **框架**: FastAPI
- **数据库**: SQLite
- **序列化**: Pickle
- **身份验证**: SHA-256 API Key
- **服务器**: Uvicorn
- **依赖管理**: Python 3.8+

## 快速开始

### 安装依赖
```bash
pip install fastapi uvicorn sqlite3 pickle hashlib uuid datetime openai
```

### 启动服务
```bash
cd CIGS
python src\cc_server.py
```

## 数据库设计
```sql
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    agent_name TEXT,
    main_purpose TEXT,
    work_description TEXT,
    writing_style TEXT,
    sample_content TEXT,
    common_phrases TEXT,
    model_selection TEXT,
    apikey TEXT,
    pkl_path TEXT,
    create_time TEXT
)
```

## API 接口文档

### 1. 创建新 Agent
**端点**  
`POST /api/agent`

**参数**  
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|-----|
| agentName | string | ✔ | Agent 名称 |
| mainPurpose | string | ✔ | 主要用途 |
| agentDescription | string | ✔ | 工作描述 |
| writingStyle | string | ✔ | 写作风格 |
| sampleContent | string | △ | 示例内容 |
| sampleContentFile | file | △ | 示例内容文本文件 (.txt) |
| commonPhrases | string | ✔ | 常用短语 |
| selectedModel | string | ✔ | 选择模型 |

**响应示例**
```json
{
    "apikey": "9f86d081...b64f",
    "url": "http://localhost:5001/agents/3d70d3e8..."
}
```

### 2. 与 Agent 交互
**端点**  
`POST /agents/{agent_id}`

**请求头**  
```
apikey: <your_api_key>
```

**请求体**
```json
{
    "user_input": "你好"
}
```

**响应示例**
```json
{
    "response": "agent test response"
}
```

### 3. 获取所有 Agent
**端点**  
`GET /agents`

**响应示例**
```json
[
    {
        "id": "3d70d3e8...",
        "agent_name": "客服助手",
        "main_purpose": "客户服务",
        ...
    }
]
```

## 核心功能实现

### Agent 创建流程
1. 生成 SHA-256 加密的 UUID
2. 初始化 Agent 对象
3. 序列化保存到 .pkl 文件
4. 存储元数据到数据库

```python
def create_agent(...):
    agent_id = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    # 对象序列化存储
    with open(pkl_path, "wb") as f:
        pickle.dump(agent, f)
    # 数据库操作
    cursor.execute("INSERT INTO agents ...")
```

### 安全机制
- 双因素验证：Agent ID + API Key
- SHA-256 加密存储
- 请求头强制 API Key 验证

```python
def load_agent(agent_id: str, apikey: str):
    cursor.execute("SELECT * FROM agents WHERE id = ? AND apikey = ?", 
                  (agent_id, apikey))
```

## 前端集成
```javascript
// 示例调用
fetch('/agents/123', {
    method: 'POST',
    headers: {
        'apikey': 'your-api-key-here',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ user_input: '你好' })
})
```

## 部署说明
1. 配置 CORS 白名单
2. 设置静态文件路径
3. 确保 agents 目录可写
4. 建议生产环境使用：
```bash
uvicorn main:app --host 0.0.0.0 --port 5001 --workers 4
```

## 注意事项
1. 开发环境前端代理配置
```javascript
// vite.config.js
server: {
    proxy: {
        '/api': 'http://localhost:5001'
    }
}
```

2. 文件存储建议
- 定期清理 .pkl 文件
- 建议实现备份机制
- 生产环境建议使用对象存储

3. 性能优化
- 添加 Redis 缓存层
- 实现数据库连接池
- 启用请求限流
```python
from fastapi.middleware import Middleware
from slowapi import Limiter
```