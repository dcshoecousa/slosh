import pytest


@pytest.mark.asyncio
async def test_current_user_can_fetch_default_settings(client) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "settings-reader@example.com",
            "full_name": "Settings Reader",
            "password": "password123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "settings-reader@example.com", "password": "password123"},
    )
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/settings/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["data"] == {
        "theme": "light",
        "sidebar_collapsed": False,
    }


@pytest.mark.asyncio
async def test_current_user_can_update_settings(client) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "settings-writer@example.com",
            "full_name": "Settings Writer",
            "password": "password123",
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "settings-writer@example.com", "password": "password123"},
    )
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_response = await client.patch(
        "/api/v1/settings/me",
        json={
            "theme": "dark",
            "sidebar_collapsed": True,
        },
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["data"] == {
        "theme": "dark",
        "sidebar_collapsed": True,
    }

    get_response = await client.get("/api/v1/settings/me", headers=headers)

    assert get_response.status_code == 200
    assert get_response.json()["data"] == {
        "theme": "dark",
        "sidebar_collapsed": True,
    }
