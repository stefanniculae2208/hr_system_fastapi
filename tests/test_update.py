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


def test_update_employee_success(mock_db_session):
    """Test updating an employee successfully."""
    mock_employee = MagicMock()
    mock_employee.id = 1
    mock_employee.first_name = "John"
    mock_employee.last_name = "Doe"
    mock_employee.email = "john.doe@example.com"
    mock_employee.gender = "Male"
    mock_employee.date_of_birth = "1990-01-01"
    mock_employee.industry = "Software"
    mock_employee.salary = 100000
    mock_employee.years_of_experience = 5
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    updated_data = {
        "first_name": "Johnathan",
        "last_name": "Doe",
        "email": "johnathan.doe@example.com",
        "gender": "Male",  # Same as before, should not be updated
        "date_of_birth": None,  # Should not be updated
        "industry": "Technology",  # Changed
        "salary": 120000,  # Increased salary
        "years_of_experience": 6  # Updated experience
    }
    response = client.put("/employees/1", json=updated_data)

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "first_name": "Johnathan",
        "last_name": "Doe",
        "email": "johnathan.doe@example.com",
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "industry": "Technology",
        "salary": 120000,
        "years_of_experience": 6
    }
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_employee)
