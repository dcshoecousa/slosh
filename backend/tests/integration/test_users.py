import pytest


async def create_token(client, email: str, password: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Seed User",
            "password": password,
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_user_crud_flow(client) -> None:
    token = await create_token(client, "owner@example.com", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/v1/users/",
        headers=headers,
        json={
            "email": "member@example.com",
            "full_name": "Member User",
            "password": "password123",
        },
    )
    assert create_response.status_code == 201
    created_user = create_response.json()["data"]
    user_id = created_user["id"]
    assert created_user["role"] == "member"

    list_response = await client.get("/api/v1/users/?skip=0&limit=10", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["data"]["total"] == 2

    get_response = await client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["data"]["email"] == "member@example.com"

    update_response = await client.patch(
        f"/api/v1/users/{user_id}",
        headers=headers,
        json={"full_name": "Updated Member", "is_active": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["full_name"] == "Updated Member"
    assert update_response.json()["data"]["is_active"] is False

    delete_response = await client.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["code"] == "success"
    assert delete_response.json()["data"] is None

    missing_response = await client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_member_cannot_access_user_management(client) -> None:
    admin_token = await create_token(client, "admin@example.com", "password123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    create_response = await client.post(
        "/api/v1/users/",
        headers=admin_headers,
        json={
            "email": "member-only@example.com",
            "full_name": "Member Only",
            "password": "password123",
        },
    )
    assert create_response.status_code == 201

    member_login = await client.post(
        "/api/v1/auth/login",
        data={"username": "member-only@example.com", "password": "password123"},
    )
    member_token = member_login.json()["data"]["access_token"]
    member_headers = {"Authorization": f"Bearer {member_token}"}

    list_response = await client.get("/api/v1/users/", headers=member_headers)
    assert list_response.status_code == 403
    assert list_response.json()["code"] == "authorization_error"
