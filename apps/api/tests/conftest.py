from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from begamer.core.config import Settings
from begamer.main import create_app


@pytest.fixture
def app(tmp_path: Path) -> FastAPI:
    return create_app(
        Settings(
            database_url=f"sqlite+aiosqlite:///{tmp_path / 'begamer-test.db'}",
            auto_create_database=True,
            seed_demo_data=True,
            steam_web_api_key=None,
            openai_api_key=None,
        )
    )


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
