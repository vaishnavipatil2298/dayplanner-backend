from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Table, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import List
from .database import Base

# Association table for task categories
task_category = Table(
    'task_category', 
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id', ondelete='CASCADE')),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'))
)

class Task(Base):
    """Task model representing a scheduled task."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    completed: Mapped[bool] = mapped_column(default=False)
    due_date: Mapped[datetime] = mapped_column(Date)
    priority: Mapped[int] = mapped_column(Integer)
    estimated_minutes: Mapped[int | None] = mapped_column(nullable=True)
    actual_minutes: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    categories: Mapped[List["Category"]] = relationship(
        secondary=task_category, 
        back_populates="tasks"
    )
    time_tracks: Mapped[List["TimeTracking"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan"
    )

class Category(Base):
    """Category model for organizing tasks."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    color: Mapped[str] = mapped_column(String(7))  # For hex color codes
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    
    tasks: Mapped[List[Task]] = relationship(secondary=task_category, back_populates="categories")
    subcategories: Mapped[List["Category"]] = relationship(cascade="all, delete-orphan")

class TimeTracking(Base):
    """Time tracking model for recording task duration."""
    __tablename__ = "time_tracking"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[float | None] = mapped_column(nullable=True)
    
    task: Mapped[Task] = relationship(back_populates="time_tracks")
