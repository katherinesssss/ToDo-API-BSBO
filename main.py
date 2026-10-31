# Главный файл приложения
from fastapi import FastAPI
from routers import tasks, stats

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={
        "name": "Екатерина",
    },
)

# Подключение роутеров к приложению.
# stats подключаем РАНЬШЕ tasks, чтобы /tasks/stats не попал
# под динамический маршрут /tasks/{task_id}.
app.include_router(stats.router)
app.include_router(tasks.router)


@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "api_title": app.title,
        "api_description": app.description,
        "api_version": app.version,
        "api_author": app.contact["name"],
    }


# Простой POST-запрос без валидации (task: dict — "что угодно").
# Нужен для демонстрации: далее его заменит модель Pydantic.
@app.post("/tasks")
async def create_task(task: dict):
    return {"message": "Запись успешно создана!", "task": task}