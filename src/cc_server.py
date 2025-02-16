from fastapi import FastAPI, File, Form, UploadFile
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
async def create_agent(
        twitterHandle: str = Form(None),  # 允许为空
        agentName: str = Form(None),  # 允许为空
        mainPurpose: str = Form(None),  # 允许为空
        workDescription: str = Form(None),  # 允许为空
        writingStyle: str = Form(None),  # 允许为空
        sampleContent: str = Form(None),  # 允许为空
        commonPhrases: str = Form(None),  # 允许为空
        avatar: UploadFile = File(None),  # 允许为空
        knowledgeBase: UploadFile = File(None)  # 允许为空 # 处理文件上传
    ):
    # 创建文件夹
    agent_folder = f"userdata/{agentName}"
    os.makedirs(agent_folder, exist_ok=True)

    # 保存文件
    avatar_path = os.path.join(agent_folder, "avatar.jpg")
    if avatar:
        with open(avatar_path, "wb") as f:
            f.write(await avatar.read())
    if knowledgeBase:
        knowledge_base_path = os.path.join(agent_folder, "knowledge_base.txt")
        with open(knowledge_base_path, "wb") as f:
            f.write(await knowledgeBase.read())

    # 保存其他字段数据到一个 JSON 文件
    agent_data = {
        "twitterHandle": twitterHandle,
        "agentName": agentName,
        "mainPurpose": mainPurpose,
        "workDescription": workDescription,
        "writingStyle": writingStyle,
        "sampleContent": sampleContent,
        "commonPhrases": commonPhrases,
    }

    # 将数据保存为 JSON 文件
    with open(os.path.join(agent_folder, "data.json"), "w") as json_file:
        json.dump(agent_data, json_file)

    # 返回给前端的响应数据
    return JSONResponse(content={
        "apikey": "test-api-key",  # 这里可以替换为实际的 API 密钥
        "url": f"http://11.0.0.0/{agent_folder}"
    })


dist_dir='dist'

app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")


# 处理根路径请求，返回 index.html
@app.get("/")
async def serve_index():
    index_path = os.path.join(dist_dir, "index.html")
    return FileResponse(index_path)



# 启动 Uvicorn 服务器
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5001)
