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
    Reset in-memory rate-limiter state and restore each limiter's
    original capacity between tests.
    """
    from app.core.rate_limit import (
        _registry,
        clear_all_limiters,
    )

    original_capacities = {
        id(limiter): limiter.max_calls
        for limiter in _registry
    }

    clear_all_limiters()

    try:
        yield
    finally:
        clear_all_limiters()

        for limiter in _registry:
            limiter.max_calls = original_capacities[id(limiter)]