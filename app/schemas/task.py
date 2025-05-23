from typing import Optional, Union, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime, timezone
import re

class TaskBase(BaseModel):
    """
    Base task schema.
    
    Attributes:
        datetime_to_do: Task execution date and time
        task_info: Task description
    """
    datetime_to_do: datetime = Field(
        ...,
        description="Task execution date and time in ISO format",
        examples=["2024-03-20T15:30:00+00:00"]
    )
    task_info: str = Field(
        ...,
        description="Task description",
        min_length=3,
        max_length=1000,
        examples=["Prepare presentation for the meeting"],
        pattern=r"^[^<>]*$"  # Disallow HTML tags
    )

    @field_validator("task_info")
    @classmethod
    def validate_task_info(cls, v: str) -> str:
        """
        Validate task description.
        
        Args:
            v: Task description
            
        Returns:
            str: Cleaned task description
            
        Raises:
            ValueError: If description contains invalid characters
        """
        v = v.strip()
        if not v:
            raise ValueError("Task description cannot be empty")
        if re.search(r"<[^>]*>", v):
            raise ValueError("Task description cannot contain HTML tags")
        return v

class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    Inherits all fields from TaskBase.
    """
    datetime_to_do: Union[datetime, str] = Field(
        ...,
        description="Task execution date and time in ISO format",
        examples=["2024-03-20T15:30:00+00:00"]
    )

    @field_validator("datetime_to_do")
    @classmethod
    def validate_datetime_to_do(cls, v: Union[datetime, str]) -> datetime:
        """
        Validate task execution date.
        
        Args:
            v: Task execution date (datetime or string)
            
        Returns:
            datetime: Validated date
            
        Raises:
            ValueError: If date is in the past or invalid format
        """
        try:
            if isinstance(v, str):
                v = datetime.fromisoformat(v)
            elif isinstance(v, datetime):
                v = v
            else:
                raise ValueError("Invalid date type")
            
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
                
            now = datetime.now(timezone.utc)
            if v < now:
                raise ValueError("Task execution date must be in the future")
                
            return v
        except ValueError as e:
            raise ValueError(f"Date validation error: {str(e)}")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "datetime_to_do": "2024-03-20T15:30:00+00:00",
                "task_info": "Prepare presentation for the meeting"
            }
        }
    )

class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    
    Attributes:
        datetime_to_do: New task execution date and time
        task_info: New task description
        is_completed: Task completion status
    """
    datetime_to_do: Optional[Union[datetime, str]] = Field(
        None,
        description="New task execution date and time",
        examples=["2024-03-20T15:30:00+00:00"]
    )
    task_info: Optional[str] = Field(
        None,
        description="New task description",
        min_length=3,
        max_length=1000,
        examples=["Updated task: prepare presentation"]
    )
    is_completed: Optional[bool] = Field(
        None,
        description="Task completion status",
        examples=[True]
    )

    @field_validator("datetime_to_do")
    @classmethod
    def validate_datetime_to_do(cls, v: Optional[Union[datetime, str]]) -> Optional[datetime]:
        if v is None:
            return None
            
        if isinstance(v, str):
            try:
                v = datetime.fromisoformat(v)
            except ValueError:
                raise ValueError("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        if v < now:
            raise ValueError("Task execution date must be in the future")
            
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "datetime_to_do": "2024-03-20T15:30:00+00:00",
                "task_info": "Updated task",
                "is_completed": True
            }
        }
    )

class Task(TaskBase):
    """
    Complete task schema, including all database fields.
    
    Attributes:
        id: Unique task identifier
        created_at: Task creation date and time
        updated_at: Last task update date and time
        user_id: Task owner user ID
        is_completed: Task completion status
    """
    id: int = Field(..., description="Unique task identifier")
    created_at: datetime = Field(..., description="Task creation date and time")
    updated_at: datetime = Field(..., description="Last task update date and time")
    user_id: int = Field(..., description="Task owner user ID")
    is_completed: bool = Field(
        default=False,
        description="Task completion status"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "datetime_to_do": "2024-03-20T15:30:00+00:00",
                "task_info": "Prepare presentation",
                "created_at": "2024-03-19T10:00:00+00:00",
                "updated_at": "2024-03-19T10:00:00+00:00",
                "user_id": 1,
                "is_completed": False
            }
        }
    )

class TaskList(BaseModel):
    """
    Schema for task list.
    
    Attributes:
        tasks: List of tasks
    """
    tasks: List[Task] = Field(
        ...,
        description="List of tasks"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "datetime_to_do": "2024-03-20T15:30:00+00:00",
                        "task_info": "Prepare presentation",
                        "created_at": "2024-03-19T10:00:00+00:00",
                        "updated_at": "2024-03-19T10:00:00+00:00",
                        "user_id": 1,
                        "is_completed": False
                    }
                ]
            }
        }
    )