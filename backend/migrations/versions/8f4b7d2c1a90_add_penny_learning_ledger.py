"""add penny learning ledger

Revision ID: 8f4b7d2c1a90
Revises: 152a2a525c7c
Create Date: 2026-09-08 08:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8f4b7d2c1a90"
down_revision: str | Sequence[str] | None = "152a2a525c7c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

IMMUTABLE_TABLES = (
    "penny_candidate_snapshots",
    "penny_market_observations",
    "penny_outcome_evaluations",
)


def upgrade() -> None:
    op.create_table(
        "penny_candidate_snapshots",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("candidate_id", sa.Uuid(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scoring_version", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("classification", sa.String(length=50), nullable=False),
        sa.Column("complete_gate_passed", sa.Boolean(), nullable=False),
        sa.Column("features_json", sa.JSON(), nullable=False),
        sa.Column("score_result_json", sa.JSON(), nullable=False),
        sa.Column("trade_plan_json", sa.JSON(), nullable=True),
        sa.Column("research_json", sa.JSON(), nullable=False),
        sa.Column("provenance_json", sa.JSON(), nullable=False),
        sa.Column("snapshot_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["scan_candidates.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_penny_candidate_snapshots_candidate_id",
        "penny_candidate_snapshots",
        ["candidate_id"],
        unique=True,
    )
    op.create_index(
        "ix_penny_candidate_snapshots_snapshot_hash",
        "penny_candidate_snapshots",
        ["snapshot_hash"],
        unique=False,
    )
    op.create_index(
        "ix_penny_candidate_snapshots_symbol",
        "penny_candidate_snapshots",
        ["symbol"],
        unique=False,
    )
    op.create_index(
        "ix_penny_snapshots_symbol_score",
        "penny_candidate_snapshots",
        ["symbol", "score"],
        unique=False,
    )
    op.create_index(
        "ix_penny_snapshots_classification_captured",
        "penny_candidate_snapshots",
        ["classification", "captured_at"],
        unique=False,
    )

    op.create_table(
        "penny_market_observations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Float(), nullable=False),
        sa.Column("high", sa.Float(), nullable=False),
        sa.Column("low", sa.Float(), nullable=False),
        sa.Column("close", sa.Float(), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("provenance", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["penny_candidate_snapshots.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "snapshot_id",
            "observed_at",
            "source",
            name="uq_penny_observation_snapshot_time_source",
        ),
    )
    op.create_index(
        "ix_penny_market_observations_snapshot_id",
        "penny_market_observations",
        ["snapshot_id"],
        unique=False,
    )
    op.create_index(
        "ix_penny_observation_snapshot_time",
        "penny_market_observations",
        ["snapshot_id", "observed_at"],
        unique=False,
    )

    op.create_table(
        "penny_outcome_evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("snapshot_id", sa.Uuid(), nullable=False),
        sa.Column("calculator_version", sa.String(length=100), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("observation_digest", sa.String(length=64), nullable=False),
        sa.Column("observation_count", sa.Integer(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["snapshot_id"],
            ["penny_candidate_snapshots.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "snapshot_id",
            "calculator_version",
            "observation_digest",
            name="uq_penny_evaluation_input_digest",
        ),
    )
    op.create_index(
        "ix_penny_outcome_evaluations_snapshot_id",
        "penny_outcome_evaluations",
        ["snapshot_id"],
        unique=False,
    )
    op.create_index(
        "ix_penny_evaluation_snapshot_created",
        "penny_outcome_evaluations",
        ["snapshot_id", "created_at"],
        unique=False,
    )

    _install_immutability_guards()


def downgrade() -> None:
    _remove_immutability_guards()

    op.drop_index(
        "ix_penny_evaluation_snapshot_created",
        table_name="penny_outcome_evaluations",
    )
    op.drop_index(
        "ix_penny_outcome_evaluations_snapshot_id",
        table_name="penny_outcome_evaluations",
    )
    op.drop_table("penny_outcome_evaluations")

    op.drop_index(
        "ix_penny_observation_snapshot_time",
        table_name="penny_market_observations",
    )
    op.drop_index(
        "ix_penny_market_observations_snapshot_id",
        table_name="penny_market_observations",
    )
    op.drop_table("penny_market_observations")

    op.drop_index(
        "ix_penny_snapshots_classification_captured",
        table_name="penny_candidate_snapshots",
    )
    op.drop_index(
        "ix_penny_snapshots_symbol_score",
        table_name="penny_candidate_snapshots",
    )
    op.drop_index(
        "ix_penny_candidate_snapshots_symbol",
        table_name="penny_candidate_snapshots",
    )
    op.drop_index(
        "ix_penny_candidate_snapshots_snapshot_hash",
        table_name="penny_candidate_snapshots",
    )
    op.drop_index(
        "ix_penny_candidate_snapshots_candidate_id",
        table_name="penny_candidate_snapshots",
    )
    op.drop_table("penny_candidate_snapshots")


def _install_immutability_guards() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        for table in IMMUTABLE_TABLES:
            op.execute(
                sa.text(
                    f"""
                    CREATE TRIGGER {table}_reject_update
                    BEFORE UPDATE ON {table}
                    BEGIN
                        SELECT RAISE(ABORT, '{table} is immutable');
                    END
                    """
                )
            )
            op.execute(
                sa.text(
                    f"""
                    CREATE TRIGGER {table}_reject_delete
                    BEFORE DELETE ON {table}
                    BEGIN
                        SELECT RAISE(ABORT, '{table} is immutable');
                    END
                    """
                )
            )
        return

    if dialect == "postgresql":
        op.execute(
            sa.text(
                """
                CREATE OR REPLACE FUNCTION penny_reject_immutable_change()
                RETURNS trigger AS $$
                BEGIN
                    RAISE EXCEPTION '% is immutable', TG_TABLE_NAME;
                END;
                $$ LANGUAGE plpgsql
                """
            )
        )
        for table in IMMUTABLE_TABLES:
            op.execute(
                sa.text(
                    f"""
                    CREATE TRIGGER {table}_reject_change
                    BEFORE UPDATE OR DELETE ON {table}
                    FOR EACH ROW EXECUTE FUNCTION penny_reject_immutable_change()
                    """
                )
            )


def _remove_immutability_guards() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "sqlite":
        for table in IMMUTABLE_TABLES:
            op.execute(sa.text(f"DROP TRIGGER IF EXISTS {table}_reject_update"))
            op.execute(sa.text(f"DROP TRIGGER IF EXISTS {table}_reject_delete"))
        return

    if dialect == "postgresql":
        for table in IMMUTABLE_TABLES:
            op.execute(
                sa.text(
                    f"DROP TRIGGER IF EXISTS {table}_reject_change ON {table}"
                )
            )
        op.execute(sa.text("DROP FUNCTION IF EXISTS penny_reject_immutable_change"))
