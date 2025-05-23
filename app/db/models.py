from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from datetime import datetime, timezone

class User(Base):
    """
    User model.
    
    Attributes:
        id: Unique user identifier
        username: Unique username
        hashed_password: Hashed password
        refresh_token: Refresh token for authentication
        is_active: User activity status
        tasks: List of user's tasks
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.username}>"

class Task(Base):
    """
    User task model.
    
    Attributes:
        id: Unique task identifier
        created_at: Task creation time
        updated_at: Last task update time
        datetime_to_do: Scheduled task execution time
        task_info: Task description
        is_completed: Task completion status
        user_id: Task owner user ID
        user: User relationship
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    datetime_to_do: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    task_info: Mapped[str] = mapped_column(String, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task {self.id}: {self.task_info[:30]}...>"

    def mark_as_completed(self) -> None:
        """Marks the task as completed."""
        self.is_completed = True
        self.updated_at = datetime.now(timezone.utc)

    def update_task_info(self, new_info: str) -> None:
        """
        Updates task information.
        
        Args:
            new_info: New task description
        """
        self.task_info = new_info
        self.updated_at = datetime.now(timezone.utc)