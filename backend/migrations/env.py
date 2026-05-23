"""Alembic environment configuration."""
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.config import settings
from app.models.model_registry import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_online() -> None:
    """Run migrations."""
    pass
