from collections.abc import Generator

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from club777_api.core.database import engine


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    nested_savepoint = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session: Session, transaction) -> None:
        nonlocal nested_savepoint
        if not nested_savepoint.is_active:
            nested_savepoint = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
