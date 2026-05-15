import pytest
from sqlalchemy import select

from app.core.rbac import build_user_subject
from app.models.casbin_rule import CasbinRule


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
async def test_member_can_read_own_permissions(client) -> None:
    await create_token(client, "admin@example.com", "password123")
    member_token = await create_token(client, "member@example.com", "password123")
    headers = {"Authorization": f"Bearer {member_token}"}

    response = await client.get("/api/v1/rbac/me/permissions", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["roles"] == ["member"]
    assert {"resource": "auth", "action": "read"} in data["permissions"]
    assert {"resource": "rbac", "action": "read"} in data["permissions"]
    assert {"resource": "rbac", "action": "check"} in data["permissions"]


@pytest.mark.asyncio
async def test_admin_can_assign_and_remove_user_role(client) -> None:
    admin_token = await create_token(client, "admin@example.com", "password123")
    member_token = await create_token(client, "member@example.com", "password123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    member_headers = {"Authorization": f"Bearer {member_token}"}

    me_response = await client.get("/api/v1/auth/me", headers=member_headers)
    member_id = me_response.json()["data"]["id"]

    assign_response = await client.post(
        f"/api/v1/rbac/users/{member_id}/roles",
        headers=admin_headers,
        json={"role": "admin"},
    )
    assert assign_response.status_code == 200
    assert assign_response.json()["data"]["roles"] == ["admin"]
    assigned_permissions = assign_response.json()["data"]["permissions"]
    assert {"resource": "users", "action": "read"} in assigned_permissions

    promoted_list_response = await client.get(
        "/api/v1/users/",
        headers=member_headers,
    )
    assert promoted_list_response.status_code == 200

    revoke_response = await client.delete(
        f"/api/v1/rbac/users/{member_id}/roles/admin",
        headers=admin_headers,
    )
    assert revoke_response.status_code == 200
    assert revoke_response.json()["data"]["roles"] == ["member"]

    downgraded_list_response = await client.get(
        "/api/v1/users/",
        headers=member_headers,
    )
    assert downgraded_list_response.status_code == 403


@pytest.mark.asyncio
async def test_assigned_user_role_is_persisted_in_casbin_grouping_rule(
    client,
    db_session,
) -> None:
    admin_token = await create_token(client, "admin@example.com", "password123")
    member_token = await create_token(client, "member@example.com", "password123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    member_headers = {"Authorization": f"Bearer {member_token}"}

    me_response = await client.get("/api/v1/auth/me", headers=member_headers)
    member_id = me_response.json()["data"]["id"]

    assign_response = await client.post(
        f"/api/v1/rbac/users/{member_id}/roles",
        headers=admin_headers,
        json={"role": "admin"},
    )

    assert assign_response.status_code == 200

    result = await db_session.execute(
        select(CasbinRule).where(
            CasbinRule.ptype == "g",
            CasbinRule.v0 == build_user_subject(member_id),
            CasbinRule.v1 == "admin",
        )
    )

    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_cannot_remove_last_admin_role(client) -> None:
    admin_token = await create_token(client, "admin@example.com", "password123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    me_response = await client.get("/api/v1/auth/me", headers=admin_headers)
    admin_id = me_response.json()["data"]["id"]

    revoke_response = await client.delete(
        f"/api/v1/rbac/users/{admin_id}/roles/admin",
        headers=admin_headers,
    )

    assert revoke_response.status_code == 409
    assert revoke_response.json()["message"] == "Cannot remove the last admin role."


@pytest.mark.asyncio
async def test_admin_can_grant_and_revoke_role_permission(client) -> None:
    admin_token = await create_token(client, "admin@example.com", "password123")
    member_token = await create_token(client, "member@example.com", "password123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    member_headers = {"Authorization": f"Bearer {member_token}"}

    before_response = await client.get(
        "/api/v1/rbac/check",
        headers=member_headers,
        params={"resource": "users", "action": "read"},
    )
    assert before_response.status_code == 200
    assert before_response.json()["data"]["allowed"] is False

    grant_response = await client.post(
        "/api/v1/rbac/roles/member/permissions",
        headers=admin_headers,
        json={"resource": "users", "action": "read"},
    )
    assert grant_response.status_code == 200
    granted_permissions = grant_response.json()["data"]["permissions"]
    assert {"resource": "users", "action": "read"} in granted_permissions

    after_grant_response = await client.get(
        "/api/v1/rbac/check",
        headers=member_headers,
        params={"resource": "users", "action": "read"},
    )
    assert after_grant_response.status_code == 200
    assert after_grant_response.json()["data"]["allowed"] is True

    revoke_response = await client.request(
        "DELETE",
        "/api/v1/rbac/roles/member/permissions",
        headers=admin_headers,
        json={"resource": "users", "action": "read"},
    )
    assert revoke_response.status_code == 200
    revoked_permissions = revoke_response.json()["data"]["permissions"]
    assert {"resource": "users", "action": "read"} not in revoked_permissions

    after_revoke_response = await client.get(
        "/api/v1/rbac/check",
        headers=member_headers,
        params={"resource": "users", "action": "read"},
    )
    assert after_revoke_response.status_code == 200
    assert after_revoke_response.json()["data"]["allowed"] is False


@pytest.mark.asyncio
async def test_granted_permission_is_persisted_in_casbin_rule_table(
    client,
    db_session,
) -> None:
    admin_token = await create_token(client, "admin@example.com", "password123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    grant_response = await client.post(
        "/api/v1/rbac/roles/member/permissions",
        headers=admin_headers,
        json={"resource": "users", "action": "read"},
    )

    assert grant_response.status_code == 200

    result = await db_session.execute(
        select(CasbinRule).where(
            CasbinRule.ptype == "p",
            CasbinRule.v0 == "member",
            CasbinRule.v1 == "users",
            CasbinRule.v2 == "read",
        )
    )

    assert result.scalar_one_or_none() is not None
