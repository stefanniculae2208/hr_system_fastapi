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


def test_get_employee_success(mock_db_session):
    """Test retrieving an employee successfully by ID."""
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
    response = client.get("/employees/1")
    
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "industry": "Software",
        "salary": 100000,
        "years_of_experience": 5
    }


def test_get_employee_not_found(mock_db_session):
    """Test retrieving an employee that does not exist (404 error)."""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None    
    response = client.get("/employees/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Employee not found"}


def test_get_employee_invalid_id(mock_db_session):
    """Test retrieving an employee with an invalid ID (non-numeric)."""
    response = client.get("/employees/abc")  # Invalid ID format (non-numeric)
    assert response.status_code == 422  # Validation error due to invalid ID format
    assert "detail" in response.json()


def test_get_all_employees_success(mock_db_session):
    """Test retrieving all employees successfully."""
    mock_employee_1 = MagicMock()
    mock_employee_1.id = 1
    mock_employee_1.first_name = "John"
    mock_employee_1.last_name = "Doe"
    mock_employee_1.email = "john.doe@example.com"
    mock_employee_1.gender = "Male"
    mock_employee_1.date_of_birth = "1990-01-01"
    mock_employee_1.industry = "Software"
    mock_employee_1.salary = 100000
    mock_employee_1.years_of_experience = 5
    
    mock_employee_2 = MagicMock()
    mock_employee_2.id = 2
    mock_employee_2.first_name = "Jane"
    mock_employee_2.last_name = "Doe"
    mock_employee_2.email = "jane.doe@example.com"
    mock_employee_2.gender = "Female"
    mock_employee_2.date_of_birth = "1985-05-15"
    mock_employee_2.industry = "Finance"
    mock_employee_2.salary = 120000
    mock_employee_2.years_of_experience = 10
    
    mock_db_session.query.return_value.all.return_value = [mock_employee_1, mock_employee_2]
    response = client.get("/employees/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    assert response.json()[0] == {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "industry": "Software",
        "salary": 100000,
        "years_of_experience": 5
    }
    assert response.json()[1] == {
        "id": 2,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "gender": "Female",
        "date_of_birth": "1985-05-15",
        "industry": "Finance",
        "salary": 120000,
        "years_of_experience": 10
    }
