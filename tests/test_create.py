import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from src.database import get_db

client = TestClient(app)

@pytest.fixture
def mock_db_session():
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    yield mock_db

@pytest.fixture(autouse=True)
def override_get_db(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session

employee_payload = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "unique.john.doe@example.com",  # Ensure this email is unique
    "gender": "Male",
    "date_of_birth": "1990-01-01",
    "industry": "Software",
    "salary": 100000,
    "years_of_experience": 5
}

def test_create_employee_success(mock_db_session):
    """Test successful employee creation."""
    response = client.post("/employees/", json=employee_payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Employee created successfully"}

def test_create_employee_invalid_data(mock_db_session):
    """Test employee creation with invalid data."""
    invalid_payload = {"first_name": ""}
    response = client.post("/employees/", json=invalid_payload)
    assert response.status_code == 422
    assert "detail" in response.json()
