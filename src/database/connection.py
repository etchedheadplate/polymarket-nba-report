from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings

SYNC_DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASS}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)


sync_engine = create_engine(SYNC_DATABASE_URL)
sync_session_maker = sessionmaker(bind=sync_engine, expire_on_commit=False)
