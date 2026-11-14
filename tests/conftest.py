from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setenv("PCR_DB_PATH", str(tmp_path / "test.sqlite3"))


@pytest.fixture(scope="session")
def service():
    from pcr.model import ModelService
    return ModelService()
