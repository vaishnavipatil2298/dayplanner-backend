from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from .core.database import engine, Base, get_db
from .core.config import INITIAL_TASKS
from .models.schemas import Task, Category, TaskStats, WorkloadStats, TaskPrediction
from .services.task_service import TaskService
from .api.routes import router

# Initialize FastAPI app
app = FastAPI(
    title="Day Planner API",
    description="API for managing daily tasks and schedules",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include API router
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Day Planner API"}

@app.get("/tasks", response_model=List[Task])
async def get_tasks(db: Session = Depends(get_db)):
    task_service = TaskService(db)
    return await task_service.get_all_tasks()

@app.post("/tasks", response_model=Task)
async def add_task(task: Task, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    return await task_service.create_task(task)

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, updated_task: Task, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    return await task_service.update_task(task_id, updated_task)

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    return await task_service.delete_task(task_id)

@app.get("/categories/{category}/workload", response_model=WorkloadStats)
async def get_category_workload(
    category: str, 
    days: int = 7, 
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return await task_service.get_category_workload(category, days)

@app.get("/tasks/{task_id}/prediction", response_model=TaskPrediction)
async def predict_task_completion(task_id: int, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    return await task_service.predict_task_completion(task_id)

@app.get("/categories/workload-balance")
async def get_workload_balance_recommendations(db: Session = Depends(get_db)):
    task_service = TaskService(db)
    return await task_service.get_workload_balance_recommendations()