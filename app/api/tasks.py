# app/api/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.db.models import Task as TaskModel
from app.services.auth_service import AuthService, get_auth_service
from app.db.models import User
from app.services.task_service import TaskService, get_task_service
import logging
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied"},
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"}
    }
)

@router.post("/create", 
    response_model=Task, 
    summary="Create a new task",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Task successfully created"},
        400: {"description": "Invalid task data"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def create_task(
    task: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(AuthService.get_current_user),
) -> Task:
    """
    Create a new task.
    
    Args:
        task: New task data
        task_service: Task service
        current_user: Current authenticated user
        
    Returns:
        Task: Created task
        
    Raises:
        HTTPException: On task creation errors
    """
    try:
        logger.info(f"Attempting to create task by user {current_user.username}")
        result = await task_service.create_task(task, current_user.id)
        logger.info(f"Task successfully created by user {current_user.username}")
        return result
    except HTTPException as e:
        logger.warning(f"Error creating task by user {current_user.username}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating task by user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating task"
        )

@router.get("/", 
    response_model=List[Task], 
    summary="Get list of tasks",
    responses={
        200: {"description": "Task list successfully retrieved"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def read_tasks(
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(AuthService.get_current_user),
) -> List[Task]:
    """
    Get list of tasks for current user.
    
    Args:
        task_service: Task service
        current_user: Current authenticated user
        
    Returns:
        List[Task]: List of user's tasks
        
    Raises:
        HTTPException: On task list retrieval errors
    """
    try:
        logger.info(f"Attempting to get task list by user {current_user.username}")
        result = await task_service.list_tasks(user_id=current_user.id)
        logger.info(f"Task list successfully retrieved by user {current_user.username}")
        return result
    except HTTPException as e:
        logger.warning(f"Error getting task list by user {current_user.username}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting task list by user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving task list"
        )

@router.get("/{task_id}", 
    response_model=Task, 
    summary="Get task by ID",
    responses={
        200: {"description": "Task successfully retrieved"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied to task"},
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"}
    }
)
async def read_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(AuthService.get_current_user),
) -> Task:
    """
    Get task by ID.
    
    Args:
        task_id: Task ID
        task_service: Task service
        current_user: Current authenticated user
        
    Returns:
        Task: Found task
        
    Raises:
        HTTPException: On task retrieval errors
    """
    try:
        logger.info(f"Attempting to get task {task_id} by user {current_user.username}")
        result = await task_service.read_task(task_id, current_user.id)
        logger.info(f"Task {task_id} successfully retrieved by user {current_user.username}")
        return result
    except HTTPException as e:
        logger.warning(f"Error getting task {task_id} by user {current_user.username}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting task {task_id} by user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving task"
        )

@router.put("/{task_id}", 
    response_model=Task, 
    summary="Update task",
    responses={
        200: {"description": "Task successfully updated"},
        400: {"description": "Invalid task data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied to task"},
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_task(
    task_id: int,
    task: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(AuthService.get_current_user),
) -> Task:
    """
    Update task.
    
    Args:
        task_id: Task ID
        task: New task data
        task_service: Task service
        current_user: Current authenticated user
        
    Returns:
        Task: Updated task
        
    Raises:
        HTTPException: On task update errors
    """
    try:
        logger.info(f"Attempting to update task {task_id} by user {current_user.username}")
        result = await task_service.update_task(task_id, task, current_user.id)
        logger.info(f"Task {task_id} successfully updated by user {current_user.username}")
        return result
    except HTTPException as e:
        logger.warning(f"Error updating task {task_id} by user {current_user.username}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating task {task_id} by user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while updating task"
        )

@router.delete("/{task_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    responses={
        204: {"description": "Task successfully deleted"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied to task"},
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(AuthService.get_current_user),
) -> None:
    """
    Delete task.
    
    Args:
        task_id: Task ID
        task_service: Task service
        current_user: Current authenticated user
        
    Raises:
        HTTPException: On task deletion errors
    """
    try:
        logger.info(f"Attempting to delete task {task_id} by user {current_user.username}")
        await task_service.delete_task(task_id, current_user.id)
        logger.info(f"Task {task_id} successfully deleted by user {current_user.username}")
    except HTTPException as e:
        logger.warning(f"Error deleting task {task_id} by user {current_user.username}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting task {task_id} by user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting task"
        )
