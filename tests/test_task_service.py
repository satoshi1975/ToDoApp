import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate
from app.db.models import Task
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

@pytest_asyncio.fixture
async def mock_session():
    """Fixture for creating AsyncSession mock object."""
    session = AsyncMock(spec=AsyncSession)
    return session

@pytest_asyncio.fixture
def task_service(mock_session):
    """Fixture for creating TaskService with mock session."""
    return TaskService(session=mock_session)

# Class for emulating SQLAlchemy execute result
class MockResult:
    def __init__(self, scalar=None, scalars=None):
        self._scalar = scalar
        self._scalars = scalars or []

    def scalar_one_or_none(self):
        return self._scalar

    def scalars(self):
        return self

    def all(self):
        return self._scalars

@pytest.mark.asyncio
async def test_create_task_success(task_service, mock_session):
    """Test successful task creation in TaskService."""
    task_create = TaskCreate(
        datetime_to_do="2026-05-23T12:00:00",
        task_info="Test task"
    )
    user_id = 1
    mock_task = Task(id=1, user_id=user_id, datetime_to_do="2025-05-23T12:00:00", task_info="Test task")
    
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    
    result = await task_service.create_task(task_create, user_id)
    
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    assert result.user_id == user_id
    assert result.task_info == "Test task"

@pytest.mark.asyncio
async def test_create_task_failure(task_service, mock_session):
    """Test error handling during task creation."""
    task_create = TaskCreate(
        datetime_to_do="2026-05-23T12:00:00",
        task_info="Test task"
    )
    user_id = 1
    mock_session.commit.side_effect = Exception("Database error")
    
    with pytest.raises(HTTPException) as exc:
        await task_service.create_task(task_create, user_id)
    assert exc.value.status_code == 500
    assert "Failed to create task: Database error" in str(exc.value.detail)
    mock_session.rollback.assert_called_once()

@pytest.mark.asyncio
async def test_read_task_success(task_service, mock_session):
    """Test successful reading of own task."""
    task_id = 1
    user_id = 1
    mock_task = Task(id=task_id, user_id=user_id, task_info="Test task", datetime_to_do="2025-05-23T12:00:00")
    mock_session.execute.return_value = MockResult(scalar=mock_task)
    
    result = await task_service.read_task(task_id, user_id)
    
    assert result.id == task_id
    assert result.user_id == user_id
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_read_task_not_found(task_service, mock_session):
    """Test reading non-existent task (404)."""
    task_id = 1
    user_id = 1
    mock_session.execute.return_value = MockResult(scalar=None)
    
    with pytest.raises(HTTPException) as exc:
        await task_service.read_task(task_id, user_id)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Task not found"
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_read_task_forbidden(task_service, mock_session):
    """Test reading another user's task (403)."""
    task_id = 1
    user_id = 1
    mock_task = Task(id=task_id, user_id=2, task_info="Test task", datetime_to_do="2025-05-23T12:00:00")
    mock_session.execute.return_value = MockResult(scalar=mock_task)
    
    with pytest.raises(HTTPException) as exc:
        await task_service.read_task(task_id, user_id)
    assert exc.value.status_code == 403
    assert exc.value.detail == "You are not allowed to read this task"
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_task_success(task_service, mock_session):
    """Test successful task update."""
    task_id = 1
    user_id = 1
    task_update = TaskUpdate(task_info="Updated task")
    mock_task = Task(id=task_id, user_id=user_id, task_info="Test task", datetime_to_do="2026-05-23T12:00:00")
    mock_session.execute.return_value = MockResult(scalar=mock_task)
    
    result = await task_service.update_task(task_id, task_update, user_id)
    
    assert result.task_info == "Updated task"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_list_tasks_all(task_service, mock_session):
    """Test getting all tasks."""
    mock_task = Task(id=1, user_id=1, task_info="Test task", datetime_to_do="2025-05-23T12:00:00")
    mock_session.execute.return_value = MockResult(scalars=[mock_task])
    
    result = await task_service.list_tasks()
    
    assert len(result) == 1
    assert result[0].task_info == "Test task"
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_list_tasks_user(task_service, mock_session):
    """Test getting tasks for specific user."""
    user_id = 1
    mock_task = Task(id=1, user_id=user_id, task_info="Test task", datetime_to_do="2025-05-23T12:00:00")
    mock_session.execute.return_value = MockResult(scalars=[mock_task])
    
    result = await task_service.list_tasks(user_id)
    
    assert len(result) == 1
    assert result[0].user_id == user_id
    mock_session.execute.assert_called_once()