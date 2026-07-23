from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    """Create all database tables registered with SQLAlchemy."""

    Base.metadata.create_all(bind=engine)
