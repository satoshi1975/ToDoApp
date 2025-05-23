from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    This class provides base functionality for all database models,
    including automatic table naming and common methods.
    """
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Automatically generates table name based on class name.
        
        Returns:
            str: Table name in lowercase
        """
        return cls.__name__.lower()
    
    def dict(self) -> dict[str, Any]:
        """
        Converts model to dictionary.
        
        Returns:
            dict[str, Any]: Dictionary with model attributes
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
