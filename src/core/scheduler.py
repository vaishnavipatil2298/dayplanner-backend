import schedule
import time
from datetime import datetime, timedelta, date
from typing import Callable, Dict, Optional, List, Any
from sqlalchemy.orm import Session
from .task_manager import Task

class TaskScheduler:
    def __init__(self):
        self.pending_tasks: Dict[str, Dict[str, Any]] = {}
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.recurring_tasks: Dict[str, Dict[str, Any]] = {}
    
    def schedule_task(
        self,
        task_name: str,
        task_func: Callable[[], bool],  # Specify return type
        scheduled_time: str,
        priority: int = 1,
        recurring: Optional[str] = None,  # 'daily', 'weekly', 'monthly'
        duration_minutes: int = 30
    ) -> bool:
        """
        Schedule a task with advanced features
        
        Args:
            task_name: Name of the task
            task_func: Function to execute, should return bool indicating success
            scheduled_time: Time in "HH:MM" format
            priority: Task priority (1-5, 1 being highest)
            recurring: Frequency of recurring task
            duration_minutes: Expected task duration in minutes
            
        Returns:
            bool: True if task was scheduled successfully
        
        Raises:
            ValueError: If priority is not between 1 and 5
        """
        if not 1 <= priority <= 5:
            raise ValueError("Priority must be between 1 and 5")

        def wrapped_task():
            try:
                # Mark task as active
                self.active_tasks[task_name] = {
                    'start_time': datetime.now(),
                    'priority': priority,
                    'duration': duration_minutes
                }
                
                # Execute task
                success = task_func()
                
                if not success:
                    # Handle unsuccessful task
                    self.pending_tasks[task_name] = {
                        'time': scheduled_time,
                        'task': task_func,
                        'priority': priority,
                        'duration': duration_minutes
                    }
                
                # Remove from active tasks
                self.active_tasks.pop(task_name, None)
                return success
                
            except Exception as e:
                print(f"Error executing task {task_name}: {e}")
                return False

        # Schedule based on recurrence
        if recurring == 'daily':
            schedule.every().day.at(scheduled_time).do(wrapped_task)
        elif recurring == 'weekly':
            schedule.every().week.at(scheduled_time).do(wrapped_task)
        elif recurring == 'monthly':
            schedule.every().month.at(scheduled_time).do(wrapped_task)
        else:
            schedule.every().day.at(scheduled_time).do(wrapped_task)
            
        # Store recurring task info
        if recurring:
            self.recurring_tasks[task_name] = {
                'frequency': recurring,
                'time': scheduled_time,
                'priority': priority
            }
        
        return True

    def cancel_task(self, task_name: str) -> bool:
        """Cancel a scheduled task"""
        try:
            # Remove from all task collections
            self.pending_tasks.pop(task_name, None)
            self.active_tasks.pop(task_name, None)
            self.recurring_tasks.pop(task_name, None)
            
            # Remove from schedule
            schedule.clear(task_name)
            return True
        except Exception as e:
            print(f"Error cancelling task {task_name}: {e}")
            return False

    def get_active_tasks(self) -> Dict:
        """Get currently running tasks"""
        return self.active_tasks

    def get_pending_tasks(self) -> Dict:
        """Get tasks that need rescheduling"""
        return self.pending_tasks

    def reschedule_pending_tasks(self) -> None:
        """Reschedule failed tasks for next available time"""
        for task_name, task_info in self.pending_tasks.items():
            # Calculate next available time slot
            next_time = self._find_next_available_slot(
                task_info['duration'],
                task_info['priority']
            )
            
            self.schedule_task(
                task_name,
                task_info['task'],
                next_time.strftime("%H:%M"),
                task_info['priority'],
                duration_minutes=task_info['duration']
            )
        self.pending_tasks.clear()

    def _find_next_available_slot(
        self,
        duration: int,
        priority: int
    ) -> datetime:
        """
        Find next available time slot based on duration and priority
        
        Args:
            duration: Task duration in minutes
            priority: Task priority level
            
        Returns:
            datetime: Next available time slot
        """
        # Simple implementation - can be enhanced with more complex logic
        next_slot = datetime.now() + timedelta(hours=1)
        return next_slot

    def run_scheduler(self) -> None:
        """Run the scheduler with error handling"""
        while True:
            try:
                schedule.run_pending()
                self.reschedule_pending_tasks()  # Check and reschedule failed tasks
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error in scheduler: {e}")
                time.sleep(60)  # Continue running even if there's an error    

    @staticmethod
    def get_tasks_for_date(db: Session, target_date: date) -> List[Task]:
        return db.query(Task).filter(Task.due_date == target_date).all()
    
    @staticmethod
    def reschedule_overdue_tasks(db: Session):
        today = date.today()
        overdue_tasks = db.query(Task).filter(
            Task.due_date < today,
            Task.completed == False
        ).all()
        
        for task in overdue_tasks:
            task.due_date = today
        
        db.commit()
        return overdue_tasks
    
    @staticmethod
    def optimize_schedule(db: Session, target_date: date) -> List[Task]:
        """
        Optimize the schedule for a given date
        
        Args:
            db: Database session
            target_date: Date to optimize schedule for
            
        Returns:
            List[Task]: Optimized list of tasks
        """
        tasks = db.query(Task).filter(
            Task.due_date == target_date,
            Task.completed == False
        ).order_by(Task.priority.desc()).all()
        
        # TODO: Implement scheduling optimization logic
        # Consider:
        # - Task priorities
        # - Task durations
        # - Working hours
        # - Breaks between tasks
        return tasks    