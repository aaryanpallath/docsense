import os

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

FAKE_EXTRACTION = {
    "vendor": "Test Vendor",
    "date": "2026-01-01",
    "total_amount": 42.5,
    "category": "Office Supplies",
    "line_items": [
        {"description": "Widget", "quantity": 1, "unit_price": 42.5, "amount": 42.5}
    ],
}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    monkeypatch.setattr(
        "app.extraction.extract_from_text", lambda text: dict(FAKE_EXTRACTION)
    )
    monkeypatch.setattr(
        "app.extraction.extract_from_image",
        lambda image_bytes, media_type: dict(FAKE_EXTRACTION),
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
