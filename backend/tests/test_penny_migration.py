from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.exc import DatabaseError

MIGRATION = (
    Path(__file__).parents[1]
    / "migrations"
    / "versions"
    / "8f4b7d2c1a90_add_penny_learning_ledger.py"
)


def load_migration() -> object:
    spec = spec_from_file_location("penny_migration", MIGRATION)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_migration_creates_ledger_and_database_immutability_guards() -> None:
    engine = sa.create_engine("sqlite:///:memory:")
    metadata = sa.MetaData()
    sa.Table(
        "scan_candidates",
        metadata,
        sa.Column("id", sa.Uuid(), primary_key=True),
    )

    with engine.begin() as connection:
        metadata.create_all(connection)
        context = MigrationContext.configure(connection)
        operations = Operations(context)
        migration = load_migration()
        migration.op = operations
        migration.upgrade()

        tables = set(sa.inspect(connection).get_table_names())
        assert {
            "penny_candidate_snapshots",
            "penny_market_observations",
            "penny_outcome_evaluations",
        }.issubset(tables)

        candidate_id = uuid4()
        snapshot_id = uuid4()
        connection.execute(
            sa.text("INSERT INTO scan_candidates (id) VALUES (:id)"),
            {"id": candidate_id.hex},
        )
        connection.execute(
            sa.text(
                """
                INSERT INTO penny_candidate_snapshots (
                    id, candidate_id, symbol, captured_at, created_at,
                    scoring_version, score, classification,
                    complete_gate_passed, features_json, score_result_json,
                    trade_plan_json, research_json, provenance_json,
                    snapshot_hash
                ) VALUES (
                    :id, :candidate_id, 'TEST', CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP, 'penny-v1', 80, 'a_tier', 1,
                    '{}', '{}', NULL, '{}', '[]', :snapshot_hash
                )
                """
            ),
            {
                "id": snapshot_id.hex,
                "candidate_id": candidate_id.hex,
                "snapshot_hash": "a" * 64,
            },
        )

        with pytest.raises(DatabaseError, match="immutable"):
            connection.execute(
                sa.text(
                    "UPDATE penny_candidate_snapshots SET score = 1 WHERE id = :id"
                ),
                {"id": snapshot_id.hex},
            )

        # The failed statement aborts only the statement in SQLite, so the
        # migration can still be downgraded in this transaction.
        migration.downgrade()
        remaining = set(sa.inspect(connection).get_table_names())
        assert "penny_candidate_snapshots" not in remaining
