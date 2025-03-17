from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.task_manager import Task, Category, TimeTracking
from pydantic import BaseModel
from datetime import date

router = APIRouter()

# Pydantic models for request/response
class TaskCreate(BaseModel):
    title: str
    due_date: date
    priority: int
    category_ids: List[int] = []

class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    due_date: date
    priority: int

    class Config:
        from_attributes = True

@router.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        title=task.title,
        due_date=task.due_date,
        priority=task.priority
    )
    
    if task.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(task.category_ids)
        ).all()
        db_task.categories = categories
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/tasks/", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Add more routes as needed
