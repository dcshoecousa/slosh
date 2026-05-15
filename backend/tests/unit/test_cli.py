import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.cli import create_user_command, main, serve_command
from app.core.rbac import build_user_subject
from app.models.casbin_rule import CasbinRule
from app.models.user import User


@pytest.mark.asyncio
async def test_create_user_command_persists_user(db_engine, monkeypatch) -> None:
    session_factory = async_sessionmaker(
        db_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    monkeypatch.setattr("app.cli.AsyncSessionLocal", session_factory)

    async def fake_close_db_connections() -> None:
        return None

    monkeypatch.setattr("app.cli.close_db_connections", fake_close_db_connections)

    await create_user_command(
        email="cli@example.com",
        password="password123",
        full_name="CLI User",
        role="admin",
        is_active=True,
    )

    async with session_factory() as session:
        user_result = await session.execute(
            select(User).where(User.email == "cli@example.com")
        )
        user = user_result.scalar_one_or_none()
        assert user is not None

        role_rule_result = await session.execute(
            select(CasbinRule).where(
                CasbinRule.ptype == "g",
                CasbinRule.v0 == build_user_subject(user.id),
                CasbinRule.v1 == "admin",
            )
        )
        role_rule = role_rule_result.scalar_one_or_none()

    assert user.full_name == "CLI User"
    assert user.is_active is True
    assert role_rule is not None


def test_serve_command_runs_uvicorn(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeUvicornModule:
        @staticmethod
        def run(app: str, **kwargs) -> None:
            captured["app"] = app
            captured.update(kwargs)

    monkeypatch.setattr(
        "app.cli.importlib.import_module",
        lambda module_name: FakeUvicornModule,
    )

    serve_command(host="127.0.0.1", port=9000, reload=True)

    assert captured["app"] == "app.main:app"
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9000
    assert captured["reload"] is True
    assert captured["factory"] is False


def test_main_dispatches_serve_command(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_serve_command(*, host: str, port: int, reload: bool) -> None:
        captured["host"] = host
        captured["port"] = port
        captured["reload"] = reload

    monkeypatch.setattr("app.cli.serve_command", fake_serve_command)

    exit_code = main(["serve", "--host", "127.0.0.1", "--port", "9100", "--reload"])

    assert exit_code == 0
    assert captured == {
        "host": "127.0.0.1",
        "port": 9100,
        "reload": True,
    }


def test_main_dispatches_create_user_command(monkeypatch) -> None:
    captured: dict[str, object] = {}

    async def fake_create_user_command(
        *,
        email: str,
        password: str,
        full_name: str | None,
        role: str,
        is_active: bool,
    ) -> None:
        captured["email"] = email
        captured["password"] = password
        captured["full_name"] = full_name
        captured["role"] = role
        captured["is_active"] = is_active

    monkeypatch.setattr("app.cli.create_user_command", fake_create_user_command)

    exit_code = main(
        [
            "create-user",
            "--email",
            "cli@example.com",
            "--password",
            "password123",
            "--full-name",
            "CLI User",
            "--role",
            "admin",
        ]
    )

    assert exit_code == 0
    assert captured == {
        "email": "cli@example.com",
        "password": "password123",
        "full_name": "CLI User",
        "role": "admin",
        "is_active": True,
    }
