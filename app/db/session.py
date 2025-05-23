from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def create_engine() -> create_async_engine:
    """
    Creates and returns an asynchronous SQLAlchemy engine.
    
    Returns:
        create_async_engine: Configured asynchronous database engine
    """
    if settings.TEST_MODE:
        return create_async_engine(
            settings.TEST_DATABASE_URL,
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            pool_pre_ping=True
        )
    
    return create_async_engine(
        url=settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        future=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_pre_ping=True,
        pool_recycle=settings.DB_POOL_RECYCLE,
        poolclass=QueuePool
    )

engine = create_engine()

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous context manager for database session.
    
    Yields:
        AsyncSession: Database session
        
    Raises:
        SQLAlchemyError: On database errors
    """
    session: Optional[AsyncSession] = None
    try:
        session = async_session()
        yield session
        await session.commit()
    except SQLAlchemyError as e:
        if session:
            await session.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        raise
    finally:
        if session:
            await session.close()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous generator for database session.
    Used in FastAPI dependency injection.
    
    Yields:
        AsyncSession: Database session
    """
    async with get_db() as session:
        yield session