"""
Alembic environment — CaM Cockpit Backend.

Usa SQLAlchemy 2.0 async com psycopg3.
A URL do banco é lida via pydantic-settings (cam._shared.config),
que carrega do .env. Nunca hardcoded aqui.
"""
from logging.config import fileConfig
import asyncio

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Lê configuração do alembic.ini
config = context.config

# Configura logging se presente no ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Lê URL do banco via settings (não de alembic.ini)
from cam._shared.config import settings  # noqa: E402

config.set_main_option("sqlalchemy.url", settings.database_url)

# Metadata para autogenerate (a ser populada quando modelos ORM forem criados)
target_metadata = None


def run_migrations_offline() -> None:
    """
    Executa migrations em modo offline (sem conexão de banco).
    Útil para gerar SQL sem um banco disponível.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Executa migrations em modo online (async, com conexão real)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Ponto de entrada para migrations online."""
    import sys

    if sys.platform == "win32":
        # Windows usa ProactorEventLoop por padrão (incompatível com psycopg async).
        # SelectorEventLoop é necessário para psycopg3 funcionar no Windows.
        import selectors

        asyncio.run(
            run_async_migrations(),
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
        )
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
