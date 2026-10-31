from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter(
    prefix="/tasks",  # все endpoints роутера будут начинаться с /tasks
    tags=["tasks"],   # группировка в Swagger UI
    responses={404: {"description": "Task not found"}},
)

# Временное хранилище (позже будет заменено на PostgreSQL)
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now(),
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now(),
    },
]


@router.get("")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db),  # количество записей в хранилище
        "tasks": tasks_db,       # всё, что есть в хранилище
    }


# ВАЖНО: конкретные маршруты (/search, /status/..., /quadrant/...) должны идти
# ДО динамического /{task_id}. Маршрут /tasks/stats вынесен в routers/stats.py
# и подключается в main.py раньше этого роутера.

@router.get("/search")
async def search_tasks(q: str = Query(..., min_length=2)) -> dict:
    # min_length=2: при слишком коротком запросе FastAPI сам вернёт 422
    keyword = q.lower()
    found_tasks = [
        task
        for task in tasks_db
        if keyword in task["title"].lower()
        or keyword in (task["description"] or "").lower()
    ]

    return {
        "query": q,
        "count": len(found_tasks),
        "tasks": found_tasks,
    }


@router.get("/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ("completed", "pending"):
        raise HTTPException(
            status_code=404,
            detail="Статус не найден. Используйте: completed или pending",
        )

    is_completed = status == "completed"
    filtered_tasks = [
        task for task in tasks_db if task["completed"] == is_completed
    ]

    return {
        "status": status,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks,
    }


@router.get("/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4",
        )

    filtered_tasks = [
        task                             # ЧТО добавляем в список
        for task in tasks_db             # ОТКУДА берём элементы
        if task["quadrant"] == quadrant  # УСЛОВИЕ фильтрации
    ]

    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks,
    }


# Динамический маршрут — строго после всех конкретных
@router.get("/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Задача с ID {task_id} не найдена",
    )