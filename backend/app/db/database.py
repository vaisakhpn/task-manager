from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# 1. Engine handles connection pool to PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Logs generated SQL queries to stdout when DEBUG=True
    pool_pre_ping=True,   # Verifies connection is alive before handing it to a request
)

# 2. SessionLocal factory produces database sessions per request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 3. Base class for all ORM models
class Base(DeclarativeBase):
    pass


# 4. Dependency generator for FastAPI routes
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
