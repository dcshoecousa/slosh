from __future__ import annotations

import argparse
import asyncio
import importlib
import sys

from app.core.exceptions import ConflictException
from app.core.rbac import get_user_role
from app.core.settings import settings
from app.db.database import AsyncSessionLocal, close_db_connections
from app.models.enums import UserRole
from app.schemas.user import UserCreate
from app.services.user_service import create_user_with_role


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project management CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_user_parser = subparsers.add_parser(
        "create-user",
        help="Create a user.",
    )
    create_user_parser.add_argument("--email", required=True, help="User email.")
    create_user_parser.add_argument(
        "--password",
        required=True,
        help="User password.",
    )
    create_user_parser.add_argument(
        "--full-name",
        default=None,
        help="User full name.",
    )
    create_user_parser.add_argument(
        "--role",
        choices=[role.value for role in UserRole],
        default=UserRole.MEMBER.value,
        help="User role.",
    )
    create_user_parser.add_argument(
        "--inactive",
        action="store_true",
        help="Create the user as inactive.",
    )

    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the API service.",
    )
    serve_parser.add_argument(
        "--host",
        default=settings.app_host,
        help="Bind host.",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=settings.app_port,
        help="Bind port.",
    )
    serve_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto reload.",
    )

    return parser


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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "create-user":
            asyncio.run(
                create_user_command(
                    email=args.email,
                    password=args.password,
                    full_name=args.full_name,
                    role=args.role,
                    is_active=not args.inactive,
                )
            )
            return 0

        if args.command == "serve":
            serve_command(
                host=args.host,
                port=args.port,
                reload=args.reload,
            )
            return 0
    except ConflictException as exc:
        print(f"Conflict: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
