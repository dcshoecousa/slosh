import pytest


@pytest.mark.asyncio
async def test_register_login_and_get_me(client) -> None:
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "full_name": "Alice",
            "password": "password123",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["code"] == "success"
    assert register_response.json()["data"]["email"] == "alice@example.com"
    assert register_response.json()["data"]["role"] == "admin"

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "alice@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["data"]["email"] == "alice@example.com"
    assert me_response.json()["data"]["role"] == "admin"


@pytest.mark.asyncio
async def test_login_with_invalid_password_returns_401(client) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "bob@example.com",
            "full_name": "Bob",
            "password": "password123",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "bob@example.com", "password": "wrong-password"},
        headers={"X-Request-ID": "req-test-auth-401"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == "authentication_error"
    assert response.json()["request_id"] == "req-test-auth-401"
    assert response.headers["X-Request-ID"] == "req-test-auth-401"
