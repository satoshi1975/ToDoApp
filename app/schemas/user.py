from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from datetime import datetime
import re

class UserBase(BaseModel):
    """
    Base user schema.
    
    Attributes:
        username: User's username
        email: User's email
    """
    username: str = Field(
        ...,
        description="User's username",
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        examples=["john_doe"]
    )
    email: EmailStr = Field(
        ...,
        description="User's email",
        examples=["user@example.com"]
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username.
        
        Args:
            v: Username
            
        Returns:
            str: Cleaned username
            
        Raises:
            ValueError: If username contains invalid characters
        """
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores and hyphens")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "user@example.com"
            }
        }
    )

class UserCreate(UserBase):
    """
    Schema for creating a new user.
    
    Attributes:
        username: User's username
        password: User's password
    """
    password: str = Field(
        ...,
        description="User's password",
        min_length=8,
        max_length=100,
        examples=["strong_password123"]
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password.
        
        Args:
            v: Password
            
        Returns:
            str: Validated password
            
        Raises:
            ValueError: If password doesn't meet security requirements
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "user@example.com",
                "password": "StrongPass123!"
            }
        }
    )

class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    
    Attributes:
        username: New username
        email: New email
        password: New password
        is_active: User's activity status
    """
    username: Optional[str] = Field(
        None,
        description="New username",
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="New email"
    )
    password: Optional[str] = Field(
        None,
        description="New password",
        min_length=8,
        max_length=100
    )
    is_active: Optional[bool] = Field(
        None,
        description="User's activity status"
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("Username cannot be empty")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores and hyphens")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "new_username",
                "email": "new.email@example.com",
                "is_active": True,
                "password": "NewStrongPass123!"
            }
        }
    )

class User(UserBase):
    """
    Complete user schema, including all database fields.
    
    Attributes:
        id: Unique user identifier
        is_active: User's activity status
        created_at: User creation date and time
        updated_at: Last user update date and time
    """
    id: int = Field(..., description="Unique user identifier")
    is_active: bool = Field(
        default=True,
        description="User's activity status"
    )
    created_at: datetime = Field(
        ...,
        description="User creation date and time"
    )
    updated_at: datetime = Field(
        ...,
        description="Last user update date and time"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "user@example.com",
                "is_active": True,
                "created_at": "2024-03-19T10:00:00+00:00",
                "updated_at": "2024-03-19T10:00:00+00:00"
            }
        }
    )

class Token(BaseModel):
    """
    Authentication token schema.
    
    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token
        token_type: Token type (always "bearer")
    """
    access_token: str = Field(
        ...,
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )
