import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import String, create_engine, inspect

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_alembic(command_args: list[str], database_url: str) -> None:
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    subprocess.run(
        [sys.executable, "-m", "alembic", *command_args],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def _schema_url(tmp_path: Path) -> str:
    return f"sqlite:///{tmp_path / 'migrations.db'}"


def test_migration_upgrades_and_schema_is_correct(tmp_path: Path) -> None:
    """Apply all migrations to a fresh SQLite DB and verify the final schema."""
    database_url = _schema_url(tmp_path)
    _run_alembic(["upgrade", "head"], database_url)

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )
    inspector = inspect(engine)

    columns = {col["name"]: col for col in inspector.get_columns("scan_candidates")}
    assert columns["instrument_id"]["nullable"] is True

    symbol_type = columns["symbol"]["type"]
    assert isinstance(symbol_type, String)
    assert symbol_type.length == 20

    foreign_keys = inspector.get_foreign_keys("scan_candidates")
    instrument_fk = next(
        (fk for fk in foreign_keys if fk["constrained_columns"] == ["instrument_id"]),
        None,
    )
    assert instrument_fk is not None
    assert instrument_fk["referred_table"] == "instruments"
    assert instrument_fk["referred_columns"] == ["id"]
    assert instrument_fk["options"].get("ondelete") == "SET NULL"

    indexes = {
        index["name"]: index for index in inspector.get_indexes("scan_candidates")
    }
    instrument_index = indexes["ix_scan_candidates_instrument_id"]
    assert instrument_index["column_names"] == ["instrument_id"]
    assert instrument_index["unique"] == 0

    unique_constraints = {
        uc["name"]: uc for uc in inspector.get_unique_constraints("scan_candidates")
    }
    assert unique_constraints["uq_scan_candidates_scan_run_instrument"][
        "column_names"
    ] == ["scan_run_id", "instrument_id"]
    assert unique_constraints["uq_scan_candidates_scan_run_symbol"]["column_names"] == [
        "scan_run_id",
        "symbol",
    ]

    engine.dispose()


def test_migration_downgrades_and_reupgrades(tmp_path: Path) -> None:
    """Confirm the target migration can be reversed and re-applied on SQLite."""
    database_url = _schema_url(tmp_path)
    _run_alembic(["upgrade", "head"], database_url)
    _run_alembic(["downgrade", "-1"], database_url)
    _run_alembic(["upgrade", "head"], database_url)

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )
    inspector = inspect(engine)

    columns = {col["name"]: col for col in inspector.get_columns("scan_candidates")}
    assert "instrument_id" in columns
    assert columns["instrument_id"]["nullable"] is True

    symbol_type = columns["symbol"]["type"]
    assert isinstance(symbol_type, String)
    assert symbol_type.length == 20

    engine.dispose()
