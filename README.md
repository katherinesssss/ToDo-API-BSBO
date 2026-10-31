# ToDo лист API

### Описание
Благодаря этому проекту можно управлять задачами с использованием матрицы Эйзенхауэра (квадранты Q1–Q4).

### Технологии
- Python 3.11
- FastAPI 0.119
- Uvicorn

### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение:
```
python -m venv venv
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
- В папке с файлом main.py выполните команду:
```
uvicorn main:app --reload
```
- Документация API: http://127.0.0.1:8000/docs

### Эндпоинты
- `GET /` — информация об API
- `GET /tasks` — список всех задач
- `GET /tasks/{task_id}` — задача по ID
- `GET /tasks/quadrant/{quadrant}` — фильтр по квадранту (Q1–Q4)
- `GET /tasks/status/{status}` — фильтр по статусу (`completed` / `pending`)
- `GET /tasks/stats` — статистика по задачам
- `GET /tasks/search?q=слово` — поиск по названию и описанию

### Автор
Екатерина
