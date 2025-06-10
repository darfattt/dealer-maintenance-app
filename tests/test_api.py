import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db, Base, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import tempfile
import os

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=test_engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=test_engine)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Dealer Dashboard API" in response.json()["message"]

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_dealer(client):
    dealer_data = {
        "dealer_id": "TEST001",
        "dealer_name": "Test Dealer",
        "api_key": "test_key",
        "api_token": "test_token"
    }
    response = client.post("/dealers/", json=dealer_data)
    assert response.status_code == 200
    assert response.json()["dealer_id"] == "TEST001"

def test_get_dealers(client):
    response = client.get("/dealers/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_fetch_configuration(client):
    # First create a dealer
    dealer_data = {
        "dealer_id": "TEST002",
        "dealer_name": "Test Dealer 2"
    }
    client.post("/dealers/", json=dealer_data)
    
    # Then create configuration
    config_data = {
        "dealer_id": "TEST002",
        "schedule_type": "daily"
    }
    response = client.post("/fetch-configurations/", json=config_data)
    assert response.status_code == 200
    assert response.json()["schedule_type"] == "daily"
