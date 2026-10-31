# Главный файл приложения
from fastapi import FastAPI, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={
        "name": "Екатерина",
    },
)


tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить практику и отправить отчёт преподавателю",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 2,
        "title": "Изучить паттерны проектирования",
        "description": "Прочитать про основные паттерны и разобрать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 3,
        "title": "Ответить на неважные письма",
        "description": "Разобрать почту и ответить на рассылки",
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 4,
        "title": "Посмотреть ленту соцсетей",
        "description": "Бесцельный просмотр ленты",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now(),
    },
]


@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "api_title": app.title,
        "api_description": app.description,
        "api_version": app.version,
        "api_author": app.contact["name"],
    }


@app.get("/tasks")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db),  # количество записей в хранилище
        "tasks": tasks_db,       # всё, что есть в хранилище
    }




@app.get("/tasks/stats")
async def get_tasks_stats() -> dict:
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    completed = 0
    pending = 0

    for task in tasks_db:
        by_quadrant[task["quadrant"]] += 1
        if task["completed"]:
            completed += 1
        else:
            pending += 1

    return {
        "total_tasks": len(tasks_db),
        "by_quadrant": by_quadrant,
        "by_status": {
            "completed": completed,
            "pending": pending,
        },
    }


@app.get("/tasks/search")
async def search_tasks(q: str) -> dict:
    keyword = q.strip()
    if len(keyword) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ключевое слово должно содержать минимум 2 символа",
        )

    keyword_lower = keyword.lower()
    found_tasks = [
        task
        for task in tasks_db
        if keyword_lower in task["title"].lower()
        or keyword_lower in (task.get("description") or "").lower()
    ]

    return {
        "query": q,
        "count": len(found_tasks),
        "tasks": found_tasks,
    }


@app.get("/tasks/status/{status_value}")
async def get_tasks_by_status(status_value: str) -> dict:
    if status_value not in ("completed", "pending"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статус не найден. Используйте: completed или pending",
        )

    is_completed = status_value == "completed"
    filtered_tasks = [
        task for task in tasks_db if task["completed"] == is_completed
    ]

    return {
        "status": status_value,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks,
    }


@app.get("/tasks/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4",
        )

    filtered_tasks = [
        task                      # ЧТО добавляем в список
        for task in tasks_db      # ОТКУДА берём элементы
        if task["quadrant"] == quadrant  # УСЛОВИЕ фильтрации
    ]

    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks,
    }

@app.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Задача с ID {task_id} не найдена",
    )
