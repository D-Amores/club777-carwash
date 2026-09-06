from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from club777_api.core.database import engine


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
