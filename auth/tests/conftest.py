import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


@pytest.fixture(scope='session')
def db_engine(request):
    """Yields a SQLAlchemy engine which is suppressed after the test session"""
    db_url = 'postgresql://user:password@localhost:5432/test_db'
    engine_ = create_engine(db_url, echo=True)

    yield engine_

    engine_.dispose()


@pytest.fixture(scope='session')
def db_session_factory(db_engine):
    """Returns a SQLAlchemy scoped session factory"""
    return scoped_session(sessionmaker(bind=db_engine))

@pytest.fixture(scope='function')
def db_session(db_session_factory):
    """Yields a SQLAlchemy connection which is rollbacked after the test"""
    session_ = db_session_factory()

    yield session_

    session_.rollback()
    session_.close()
