from app.schemas.task import TaskEnqueueRead, TaskResultRead, TaskStatusRead


async def _register_and_login(client, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Task Runner",
            "password": "password123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"},
    )
    return login_response.json()["data"]["access_token"]


async def test_echo_task_endpoint_returns_queued_task(client, monkeypatch) -> None:
    token = await _register_and_login(client, "task-echo@example.com")

    async def fake_enqueue_echo_task(
        *,
        message: str,
        requested_by: int,
    ) -> TaskEnqueueRead:
        assert message == "hello queue"
        assert requested_by > 0
        return TaskEnqueueRead(task_id="task-123", task_name="tasks.echo")

    monkeypatch.setattr(
        "app.api.v1.endpoints.tasks.enqueue_echo_task",
        fake_enqueue_echo_task,
    )

    response = await client.post(
        "/api/v1/tasks/echo",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "hello queue"},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["data"]["task_id"] == "task-123"
    assert body["data"]["task_name"] == "tasks.echo"
    assert body["data"]["status"] == "queued"


async def test_task_status_endpoint_returns_completed_result(
    client,
    monkeypatch,
) -> None:
    token = await _register_and_login(client, "task-status@example.com")

    async def fake_get_task_result(
        *,
        task_id: str,
        wait: bool = False,
        timeout_seconds: float | None = None,
    ) -> TaskStatusRead:
        assert task_id == "task-456"
        assert wait is True
        assert timeout_seconds == 2.0
        return TaskStatusRead(
            task_id=task_id,
            status="completed",
            details=TaskResultRead(
                is_err=False,
                execution_time=0.12,
                result={"message": "done"},
                error=None,
            ),
        )

    monkeypatch.setattr(
        "app.api.v1.endpoints.tasks.get_task_result",
        fake_get_task_result,
    )

    response = await client.get(
        "/api/v1/tasks/task-456?wait=true&timeout_seconds=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["task_id"] == "task-456"
    assert body["data"]["status"] == "completed"
    assert body["data"]["details"]["result"] == {"message": "done"}
