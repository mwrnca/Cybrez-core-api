import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.config.settings import settings

TEST_DATABASE_URL = (
    "postgresql+psycopg://postgres:p47uk3p47uk3@localhost:5432/cybrez_test"
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db):
    secure_cookie = settings.REFRESH_COOKIE_SECURE
    settings.REFRESH_COOKIE_SECURE = False

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as c:
            yield c
    finally:
        settings.REFRESH_COOKIE_SECURE = secure_cookie
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """
    Reset all in-memory rate-limiter state before and after each test.

    This prevents rate-limit counters from leaking between test functions
    (the limiter instances are module-level singletons).  Without this,
    tests that make several auth/search calls could inadvertently trigger
    the limit and cause subsequent tests to fail.
    """
    from app.core.rate_limit import clear_all_limiters
    clear_all_limiters()
    yield
    clear_all_limiters()