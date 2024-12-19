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


def test_delete_employee_success(mock_db_session):
    """Test deleting an employee successfully."""
    mock_employee = MagicMock()
    mock_employee.id = 1
    mock_employee.first_name = "John"
    mock_employee.last_name = "Doe"
    mock_employee.email = "john.doe@example.com"
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_employee
    response = client.delete("/employees/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Employee deleted successfully"}
    mock_db_session.delete.assert_called_once_with(mock_employee)
    mock_db_session.commit.assert_called_once()


def test_delete_employee_not_found(mock_db_session):
    """Test trying to delete an employee that does not exist (404 error)."""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    response = client.delete("/employees/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}
