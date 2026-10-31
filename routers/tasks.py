from fastapi import APIRouter, HTTPException, Query
from fastapi import Response, status
from typing import List, Dict, Any
from datetime import datetime

from schemas import TaskBase, TaskCreate, TaskUpdate, TaskResponse
from database import tasks_db

router = APIRouter(
    prefix="/tasks",  # все endpoints роутера будут начинаться с /tasks
    tags=["tasks"],   # группировка в Swagger UI
    responses={404: {"description": "Task not found"}},
)


def calculate_quadrant(is_important: bool, is_urgent: bool) -> str:
    """Определяет квадрант матрицы Эйзенхауэра."""
    if is_important and is_urgent:
        return "Q1"
    elif is_important and not is_urgent:
        return "Q2"
    elif not is_important and is_urgent:
        return "Q3"
    else:
        return "Q4"


def find_task(task_id: int) -> Dict[str, Any]:
    """Ищет задачу по ID, при отсутствии — 404."""
    task = next((t for t in tasks_db if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.get("")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db),  # количество записей в хранилище
        "tasks": tasks_db,       # всё, что есть в хранилище
    }


# ВАЖНО: конкретные маршруты (/search, /status/..., /quadrant/...) должны идти
# ДО динамического /{task_id}.

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


@router.get("/status/{status_value}")
async def get_tasks_by_status(status_value: str) -> dict:
    if status_value not in ("completed", "pending"):
        raise HTTPException(
            status_code=404,
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


# Динамический маршрут — после всех конкретных GET-маршрутов
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int) -> TaskResponse:
    return find_task(task_id)


# POST: создание задачи.
# response_model=TaskResponse — ответ будет соответствовать схеме
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate) -> TaskResponse:
    # Определяем квадрант
    quadrant = calculate_quadrant(task.is_important, task.is_urgent)

    new_id = max([t["id"] for t in tasks_db], default=0) + 1  # новый ID

    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "is_important": task.is_important,
        "is_urgent": task.is_urgent,
        "quadrant": quadrant,
        "completed": False,
        "created_at": datetime.now(),
    }

    tasks_db.append(new_task)  # "Сохраняем" в нашу "базу данных"

    # FastAPI автоматически преобразует dict в Pydantic-модель TaskResponse
    return new_task


# PUT: обновление задачи (передаются только изменяемые поля)
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    # ШАГ 1: ищем задачу по ID
    task = find_task(task_id)

    # ШАГ 2: обновляем только переданные поля (exclude_unset=True)
    # Без exclude_unset=True все None-поля тоже попадут в словарь
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        task[field] = value

    # ШАГ 3: пересчитываем квадрант, если изменились важность или срочность
    if "is_important" in update_data or "is_urgent" in update_data:
        task["quadrant"] = calculate_quadrant(
            task["is_important"], task["is_urgent"]
        )

    return task


# PATCH: отметить задачу выполненной (с датой выполнения)
@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: int) -> TaskResponse:
    task = find_task(task_id)

    task["completed"] = True
    task["completed_at"] = datetime.now()

    return task


# DELETE: удаление задачи. По REST-стандарту — 204 No Content (без тела)
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    task = find_task(task_id)

    tasks_db.remove(task)

    return Response(status_code=status.HTTP_204_NO_CONTENT)