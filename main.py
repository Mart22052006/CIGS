from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cigs.routers.agent_router import router as agent_router
from cigs.playground.router import get_playground_router

app = FastAPI()

# Подключение CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(agent_router, tags=["Agent"])

# Создание роутера для Playground (необходимы параметры: agents и workflows)
agents = []  # Тут укажите список агентов
workflows = []  # Тут укажите список рабочих процессов
playground_router = get_playground_router(agents, workflows)
app.include_router(playground_router, prefix="/playground", tags=["Playground"])

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=True)
