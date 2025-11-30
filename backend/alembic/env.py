"""Alembic环境配置"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# 添加项目路径以便导入models
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 导入所有models
from app.core.database import Base
from app.models import user, subscription, stock

# Alembic Config对象
config = context.config

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置target metadata (所有表的定义)
target_metadata = Base.metadata

# 从环境变量读取数据库URL
from app.core.config import settings
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """离线模式迁移（生成SQL文件）"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式迁移（直接连接数据库）"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
