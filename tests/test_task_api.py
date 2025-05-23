import pytest
from fastapi.testclient import TestClient
from app.schemas.task import TaskCreate, TaskUpdate
from app.db.models import Task, User
from datetime import datetime

@pytest.mark.asyncio
async def test_create_task_success(client: TestClient, access_token, test_user):
    """Тест успешного создания задачи."""
    task_data = {
        "datetime_to_do": "2026-05-23T12:00:00+00:00",
        "task_info": "Test task"
    }
    response = client.post(
        "/tasks/create",
        json=task_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["task_info"] == "Test task"
    assert data["user_id"] == test_user.id

@pytest.mark.asyncio
async def test_create_task_unauthorized(client: TestClient):
    """Тест создания задачи без токена (401)."""
    task_data = {
        "datetime_to_do": "2025-05-23T12:00:00+00:00",
        "task_info": "Test task"
    }
    response = client.post("/tasks/create", json=task_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

@pytest.mark.asyncio
async def test_read_task_success(client: TestClient, access_token, test_task, test_user):
    """Тест успешного чтения своей задачи."""
    response = client.get(
        f"/tasks/{test_task.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_task.id
    assert data["task_info"] == test_task.task_info
    assert data["user_id"] == test_user.id

@pytest.mark.asyncio
async def test_read_task_not_found(client: TestClient, access_token):
    """Тест чтения несуществующей задачи (404)."""
    response = client.get(
        "/tasks/999",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

@pytest.mark.asyncio
async def test_read_task_forbidden(client: TestClient, test_session, access_token, test_user):
    """Тест чтения чужой задачи (403)."""
    other_user = User(username="otheruser", hashed_password="fake_hashed_password")
    test_session.add(other_user)
    await test_session.commit()
    await test_session.refresh(other_user)
    
    other_task = Task(
        user_id=other_user.id,
        datetime_to_do=datetime.fromisoformat("2025-05-23T12:00:00"),
        task_info="Other task",
        created_at=datetime.fromisoformat("2025-05-23T10:00:00"),
        updated_at=datetime.fromisoformat("2025-05-23T10:00:00")
    )
    test_session.add(other_task)
    await test_session.commit()
    
    response = client.get(
        f"/tasks/{other_task.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not allowed to read this task"

@pytest.mark.asyncio
async def test_update_task_success(client: TestClient, access_token, test_task):
    """Тест успешного обновления своей задачи."""
    update_data = {
        "task_info": "Updated task"
    }
    response = client.put(
        f"/tasks/{test_task.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_info"] == "Updated task"
    assert data["id"] == test_task.id

@pytest.mark.asyncio
async def test_update_task_not_found(client: TestClient, access_token):
    """Тест обновления несуществующей задачи (404)."""
    update_data = {"task_info": "Updated task"}
    response = client.put(
        "/tasks/999",
        json=update_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

@pytest.mark.asyncio
async def test_list_tasks(client: TestClient, access_token, test_task, test_user):
    """Тест получения списка задач пользователя."""
    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(task["id"] == test_task.id for task in data)
    assert all(task["user_id"] == test_user.id for task in data)