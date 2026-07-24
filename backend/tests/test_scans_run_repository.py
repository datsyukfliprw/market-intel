from sqlalchemy.orm import Session

from app.models.scan_run import ScanRunStatus
from app.repositories.scan_run import ScanRunRepository


def test_create_and_retrieve_scan_run(
    session: Session,
) -> None:
    repository = ScanRunRepository(session)

    created = repository.create("momentum_breakout")
    session.commit()
    session.refresh(created)

    retrieved = repository.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.strategy_name == "momentum_breakout"
    assert retrieved.status == ScanRunStatus.PENDING
    assert retrieved.candidates_found == 0


def test_list_scan_runs(session: Session) -> None:
    repository = ScanRunRepository(session)

    repository.create("momentum_breakout")
    repository.create("earnings_reversal")
    session.commit()

    scan_runs = repository.list_all()

    assert len(scan_runs) == 2

    assert {scan_run.strategy_name for scan_run in scan_runs} == {
        "momentum_breakout",
        "earnings_reversal",
    }
