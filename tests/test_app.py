import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as app_module

@pytest.fixture
def client(tmp_path, monkeypatch):
    db=tmp_path/"test.db"
    monkeypatch.setattr(app_module,"DB_PATH",db)
    app_module.init_db()
    app_module.app.config["TESTING"]=True
    with app_module.app.test_client() as client:
        yield client

def test_home_page(client):
    response=client.get("/")
    assert response.status_code==200
    assert b"DailyLife Manager" in response.data

def test_health_endpoint(client):
    response=client.get("/health")
    assert response.status_code==200
    assert response.get_json()["status"]=="healthy"

def test_add_task(client):
    response=client.post("/tasks",data={"title":"Complete Python practice","priority":"High","due_date":"2026-09-16"},follow_redirects=True)
    assert response.status_code==200
    assert b"Complete Python practice" in response.data
