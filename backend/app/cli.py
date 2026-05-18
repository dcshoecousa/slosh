from __future__ import annotations

import asyncio
import importlib
import sys
from typing import Annotated

import typer

from app.core.exceptions import ConflictException
from app.core.rbac import get_user_role
from app.core.settings import settings
from app.db.database import AsyncSessionLocal, close_db_connections
from app.models.enums import UserRole
from app.schemas.user import UserCreate
from app.services.user_service import create_user_with_role

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Project management CLI.",
)


async def create_user_command(
    *,
    email: str,
    password: str,
    full_name: str | None,
    role: str,
    is_active: bool,
) -> None:
    async with AsyncSessionLocal() as session:
        try:
            user = await create_user_with_role(
                session,
                UserCreate(
                    email=email,
                    password=password,
                    full_name=full_name,
                    is_active=is_active,
                ),
                role=UserRole(role),
            )
            assigned_role = await get_user_role(session, user.id)
            await session.commit()
        except Exception:
            if session.in_transaction():
                await session.rollback()
            raise
        finally:
            await close_db_connections()

    print(
        "User created successfully: "
        f"id={user.id}, email={user.email}, role={assigned_role.value}."
    )


def serve_command(
    *,
    host: str,
    port: int,
    reload: bool,
) -> None:
    uvicorn = importlib.import_module("uvicorn")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        factory=False,
    )


@app.command("create-user")
def create_user_cli(
    email: Annotated[str, typer.Option(help="User email.")],
    password: Annotated[str, typer.Option(help="User password.")],
    full_name: Annotated[
        str | None,
        typer.Option(help="User full name."),
    ] = None,
    role: Annotated[
        UserRole,
        typer.Option(
            case_sensitive=False,
            help="User role.",
        ),
    ] = UserRole.MEMBER,
    inactive: Annotated[
        bool,
        typer.Option(help="Create the user as inactive."),
    ] = False,
) -> None:
    asyncio.run(
        create_user_command(
            email=email,
            password=password,
            full_name=full_name,
            role=role.value,
            is_active=not inactive,
        )
    )


@app.command("serve")
def serve_cli(
    host: Annotated[
        str,
        typer.Option(help="Bind host."),
    ] = settings.app_host,
    port: Annotated[
        int,
        typer.Option(help="Bind port."),
    ] = settings.app_port,
    reload: Annotated[
        bool,
        typer.Option(help="Enable auto reload."),
    ] = False,
) -> None:
    serve_command(
        host=host,
        port=port,
        reload=reload,
    )


def main(argv: list[str] | None = None) -> int:
    try:
        app(
            args=argv,
            standalone_mode=False,
            prog_name="python -m app.cli",
        )
        return 0
    except ConflictException as exc:
        print(f"Conflict: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
