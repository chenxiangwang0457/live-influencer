# backend/tests/influencer/conftest.py
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from deerflow.persistence.base import Base


@pytest.fixture
def db_session():
    """Provide a sync in-memory SQLite session for influencer model tests."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
