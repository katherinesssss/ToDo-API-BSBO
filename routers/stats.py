from fastapi import APIRouter

from database import tasks_db  # единое хранилище задач

router = APIRouter(
    prefix="/stats",      # все endpoints роутера начинаются с /stats
    tags=["statistics"],  # отдельная группа в Swagger UI
)


@router.get("/")
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