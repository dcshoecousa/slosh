from taskiq_postgresql import PostgresqlBroker, PostgresqlResultBackend

from app.core.logging import get_logger
from app.core.settings import settings

logger = get_logger(__name__)

result_backend = PostgresqlResultBackend(
    dsn=lambda: settings.taskiq_dsn,
    keep_results=settings.taskiq_keep_results,
    table_name=settings.taskiq_result_table_name,
    driver="asyncpg",
    run_migrations=False,
)

broker = PostgresqlBroker(
    dsn=lambda: settings.taskiq_dsn,
    table_name=settings.taskiq_message_table_name,
    channel_name=settings.taskiq_channel_name,
    driver="asyncpg",
    run_migrations=False,
).with_result_backend(result_backend)


async def startup_taskiq() -> None:
    if getattr(broker.state, "is_client_running", False):
        return

    await broker.startup()
    broker.state.is_client_running = True
    logger.info(
        "Taskiq broker started. enabled={}, channel={}",
        settings.taskiq_enabled,
        settings.taskiq_channel_name,
    )


async def shutdown_taskiq() -> None:
    if not getattr(broker.state, "is_client_running", False):
        return

    await broker.shutdown()
    broker.state.is_client_running = False
    logger.info("Taskiq broker stopped.")
