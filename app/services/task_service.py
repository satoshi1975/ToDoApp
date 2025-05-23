from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.db.session import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.db.models import Task as TaskModel
import logging
from fastapi import Query

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class TaskService:
    """Service for working with tasks."""

    def __init__(
        self,
        session: AsyncSession,
    ):
        """
        Initialize task service.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def create_task(self, task: TaskCreate, user_id: int) -> Task:
        """
        Create a new task.
        
        Args:
            task: Task creation data
            user_id: User ID
            
        Returns:
            Task: Created task
            
        Raises:
            HTTPException: On task creation error
        """
        try:
            db_task = TaskModel(**task.model_dump(), user_id=user_id)
            self.session.add(db_task)
            await self.session.commit()
            await self.session.refresh(db_task)
            return db_task
        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create task: {str(e)}"
            )

    async def read_task(self, task_id: int, user_id: int) -> Task:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            user_id: User ID
            
        Returns:
            Task: Found task
            
        Raises:
            HTTPException: If task not found or no access
        """
        try:
            task_query = await self.session.execute(
                select(TaskModel).filter(TaskModel.id == task_id)
            )
            task = task_query.scalar_one_or_none()
            
            if task is None:
                raise HTTPException(status_code=404, detail="Task not found")
            if task.user_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="You are not allowed to read this task"
                )
            return task
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reading task: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    async def update_task(
        self,
        task_id: int,
        task_update: TaskUpdate,
        user_id: int
    ) -> Task:
        """
        Update task.
        
        Args:
            task_id: Task ID
            task_update: Update data
            user_id: User ID
            
        Returns:
            Task: Updated task
            
        Raises:
            HTTPException: If task not found or no access
        """
        try:
            task_query = await self.session.execute(
                select(TaskModel).filter(TaskModel.id == task_id)
            )
            task = task_query.scalar_one_or_none()
            
            if task is None:
                raise HTTPException(status_code=404, detail="Task not found")
            if task.user_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="You are not allowed to update this task"
                )
                
            update_data = task_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(task, key, value)
                
            await self.session.commit()
            await self.session.refresh(task)
            return task
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )

    async def list_tasks(
        self,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Task]:
        """
        Get list of tasks with pagination.
        
        Args:
            user_id: User ID (optional)
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List[Task]: List of tasks
        """
        try:
            query = select(TaskModel)
            if user_id is not None:
                query = query.filter(TaskModel.user_id == user_id)
            
            query = query.offset(skip).limit(limit)
            tasks_query = await self.session.execute(query)
            return tasks_query.scalars().all()
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )


def get_task_service(session: AsyncSession = Depends(get_db)) -> TaskService:
    """
    Factory for creating TaskService instance.
    
    Args:
        session: SQLAlchemy async session
        
    Returns:
        TaskService: Task service instance
    """
    return TaskService(session)