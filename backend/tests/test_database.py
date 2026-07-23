from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import create_database_engine


def test_sqlite_database_connection(tmp_path: Path) -> None:
    database_path = tmp_path / "test_market_intel.db"
    database_url = f"sqlite:///{database_path}"

    engine = create_database_engine(database_url)

    with Session(engine) as session:
        result = session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1

    engine.dispose()
