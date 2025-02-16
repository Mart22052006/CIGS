import sys
import os
from cigs.agent import Agent
from cigs.model.openai import OpenAIChat
from cigs.model.openrouter import OpenRouter
from cigs.tools.duckduckgo import DuckDuckGo
# from quart_openrouter.personality import Agent1Personality
# from quart_openrouter.ai_client import AIClient
# from quart_openrouter.ai_client import OpenRouterClient
import os
import asyncio
from typing import List
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json
import shutil
from typing import Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
import sqlite3
import uuid
import os
from datetime import datetime
import pickle
import hashlib

def init_db():
    conn = sqlite3.connect("agents.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
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
    """)
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# Iterate over scenarios and get responses
def create_agent(agent_name,main_purpose,work_description,writing_style,sample_content,common_phrases,model_selection):
    # 生成唯一 ID 和 API Key
    agent_id = str(uuid.uuid4())
    apikey = str(uuid.uuid4())
    agent_id = hashlib.sha256(agent_id.encode()).hexdigest()
    apikey = hashlib.sha256(apikey.encode()).hexdigest()
    agent = Agent(
        name=agent_name,
        model=OpenRouter(id="qwen/qwen-vl-plus:free"),
        # model=OpenAIChat(id="gpt-4o"),
        # tools=[DuckDuckGo()],
        description=main_purpose,
        introduction=work_description,
        system_prompt=f'Your name is {agent_name},here is the rules and informations you can use:'+'Writing Style:'+writing_style+'Sample Content:'+sample_content+'Common Phrases: '+common_phrases,
        # show_tool_calls=True,new_messages[0].get('content')+
        add_history_to_messages=True,
        num_history_responses=5,
        use_memory=True,
        markdown=True,
    )

    # 保存 Agent 对象到 .pkl 文件
    pkl_path = f"agents/{agent_id}.pkl"
    os.makedirs(os.path.dirname(pkl_path), exist_ok=True)
    with open(pkl_path, "wb") as f:
        pickle.dump(agent, f)

    # 插入数据到数据库
    conn = sqlite3.connect("agents.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO agents (
            id, agent_name, main_purpose, work_description, writing_style,
            sample_content, common_phrases, model_selection, 
            apikey, pkl_path, create_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        agent_id, agent_name, main_purpose, work_description, writing_style,
        sample_content, common_phrases, model_selection,
        apikey, pkl_path, datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

    return {
        "id": agent_id,
        "apikey": apikey,
        "pkl_path": pkl_path
    }

def load_agent(agent_id: str, apikey: str):
    conn = sqlite3.connect("agents.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents WHERE id = ? AND apikey = ?", (agent_id, apikey))
    agent_data = cursor.fetchone()
    conn.close()

    if not agent_data:
        return None

    # 读取 .pkl 文件
    pkl_path = agent_data[9]  # pkl_path 是第 10 个字段
    with open(pkl_path, "rb") as f:
        agent = pickle.load(f)

    return agent, pkl_path

def update_agent_pkl(agent, pkl_path):
    with open(pkl_path, "wb") as f:
        pickle.dump(agent, f)


app = FastAPI()
origins = [
    "http://localhost:5173",  # 前端开发环境地址
    "http://localhost",       # 可以添加 localhost 的其他可能来源
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方法
    allow_headers=["*"],  # 允许所有请求头
)

# 定义返回的JSON模型
class AgentResponse(BaseModel):
    apikey: str
    url: str



@app.post("/api/agent")
async def agent_request(
        agentName: str = Form(None),
        mainPurpose: str = Form(None),  
        agentDescription: str = Form(None), 
        writingStyle: str = Form(None), 
        sampleContent: str = Form(None), 
        sampleContentFile:UploadFile = File(None) ,
        commonPhrases: str = Form(None), 
        selectedModel: str = Form(None),

    ):
    print(selectedModel)
    # 如果上传了sampleContentFile，则使用sampleContentFile中的内容
    if sampleContentFile:
        # 检查文件类型是否为txt
        if sampleContentFile.content_type != "text/plain":
            raise HTTPException(status_code=400, detail="File must be a text file (.txt)")
        
        # 读取文件内容
        content = await sampleContentFile.read()
        sampleContent = content.decode("utf-8")

    agent_data = create_agent(agentName,mainPurpose,agentDescription,writingStyle,sampleContent,commonPhrases,selectedModel)


    # 返回给前端的响应数据
    return JSONResponse(content={
        "apikey": agent_data["apikey"],
        "url": f"http://localhost:5001/agents/{agent_data['id']}"
    })

# 定义请求体模型
class AgentRequest(BaseModel):
    user_input: str

# 访问 Agent 的 API 端点
@app.post("/agents/{agent_id}")
async def agent_response_endpoint(
    agent_id: str,
    request: AgentRequest,
    apikey: str = Header(..., description="API Key for authentication")
):
    # 加载 Agent
    result = load_agent(agent_id, apikey)
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found or API Key is invalid")

    agent, pkl_path = result

    # 生成回答
    response = agent.run(request.user_input)
    response = response.content

    # response = 'agent test response'
    # 更新 .pkl 文件（假设 Agent 对象的状态可能发生变化）
    update_agent_pkl(agent, pkl_path)

    return JSONResponse(content={"response": response})


dist_dir='dist'
app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")

# 处理根路径请求，返回 index.html
@app.get("/")
async def serve_index():
    index_path = os.path.join(dist_dir, "index.html")
    return FileResponse(index_path)


def get_db():
    conn = sqlite3.connect("agents.db")
    cursor = conn.cursor()
    return conn, cursor


class Agent_data(BaseModel):
    id: str
    agent_name: str
    main_purpose: str
    work_description: Optional[str]
    writing_style: str
    sample_content: str
    common_phrases: str
    model_selection: str
    apikey: str
    pkl_path: str
    create_time: str

@app.get("/agents", response_model=List[Agent_data])
def get_agents():
    conn, cursor = get_db()
    cursor.execute("SELECT * FROM agents")
    rows = cursor.fetchall()
    conn.close()
    return [Agent_data(**dict(zip(
        ["id", "agent_name", "main_purpose", "work_description", "writing_style",
         "sample_content", "common_phrases", "model_selection", "apikey", "pkl_path", "create_time"],
        row))) for row in rows]

@app.put("/agents/{agent_id}")
def update_agent(agent_id: str, updated_data: dict):
    conn, cursor = get_db()
    
    # 构造 SQL 语句
    columns = ", ".join([f"{key} = ?" for key in updated_data.keys()])
    values = list(updated_data.values()) + [agent_id]
    
    cursor.execute(f"UPDATE agents SET {columns} WHERE id = ?", values)
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"message": "Agent updated successfully"}


# 启动 Uvicorn 服务器
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5001)
