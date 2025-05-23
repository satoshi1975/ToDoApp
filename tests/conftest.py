import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import engine, async_session
from app.db.models import Base, User, Task
from app.services.auth_service import AuthService
from app.core.config import Settings
from app.db.session import get_db
from datetime import datetime

# Test database settings (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
settings = Settings(DATABASE_URL=TEST_DATABASE_URL, SECRET_KEY="12345678901234567890123456789012")

@pytest_asyncio.fixture
async def test_session():
    """Fixture for creating test AsyncSession and initializing database."""
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with async_session() as session:
        yield session
    
    # Drop all tables after use
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(test_session):
    """Fixture for FastAPI TestClient with get_db override."""
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_user(test_session):
    """Fixture for creating test user."""
    user = User(
        username="testuser",
        hashed_password="fake_hashed_password"  # Simplified, without real hashing
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def access_token(test_user, test_session):
    """Fixture for creating JWT token for test user."""
    auth_service = AuthService(session=test_session)
    return await auth_service.create_access_token(data={"sub": test_user.username})

@pytest_asyncio.fixture
async def test_task(test_session, test_user):
    """Fixture for creating test task."""
    task = Task(
        user_id=test_user.id,
        datetime_to_do=datetime.fromisoformat("2025-05-23T12:00:00+00:00"),
        task_info="Test task",
        created_at=datetime.fromisoformat("2025-05-23T10:00:00+00:00"),
        updated_at=datetime.fromisoformat("2025-05-23T10:00:00+00:00")
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    return task