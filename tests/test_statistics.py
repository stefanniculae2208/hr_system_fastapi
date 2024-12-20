import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from src.database import get_db
import pandas as pd

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


# Test case for average_age_by_industry
def test_average_age_by_industry(mock_db_session):
    """Test for /average_age_by_industry endpoint."""
    mock_db_session.query.return_value.all.return_value = [
        (1, "IT", "1990-01-01"),
        (2, "IT", "1985-05-05"),
        (3, "HR", "1992-07-07"),
        (4, "HR", "1988-08-08"),
        (5, "HR", "1990-01-01"),
        (6, "HR", "1988-08-09"),
    ]
    def mock_calculate_age(dob):
        return 30 if dob == "1990-01-01" else 35
    from src import utils
    utils.calculate_age = mock_calculate_age
    response = client.get("/get_statistics?stat=average_age_by_industry")
    
    assert response.status_code == 200
    assert response.json() == [
        {"industry": "HR", "average_age": 33.75},
        {"industry": "IT", "average_age": 32.5},
    ]


def test_average_salary_by_industry(mock_db_session):
    """Test for /average_salary_by_industry endpoint."""
    mock_db_session.query.return_value.all.return_value = [
        (1, "IT", 100000),
        (2, "IT", 120000),
        (3, "HR", 60000),
        (4, "HR", 70000),
    ]
    response = client.get("/get_statistics?stat=average_salary_by_industry")
    
    assert response.status_code == 200
    assert response.json() == [
        {"industry": "HR", "average_salary": 65000.0},
        {"industry": "IT", "average_salary": 110000.0},
    ]


def test_average_salary_by_experience(mock_db_session):
    """Test for /average_salary_by_experience endpoint."""
    mock_db_session.query.return_value.all.return_value = [
        (1, 5, 50000),
        (2, 10, 60000),
        (3, 5, 55000),
        (4, 15, 70000),
    ]
    response = client.get("/get_statistics?stat=average_salary_by_experience")

    assert response.status_code == 200
    assert response.json() == [
        {"years_of_experience": 5, "average_salary": 52500.0},
        {"years_of_experience": 10, "average_salary": 60000.0},
        {"years_of_experience": 15, "average_salary": 70000.0}
    ]


def test_gender_distribution_per_industry(mock_db_session):
    """Test for /gender_distribution_per_industry endpoint."""
    mock_db_session.query.return_value.all.return_value = [
        (1, "Male", "IT"),
        (2, "Female", "IT"),
        (3, "Male", "HR"),
        (4, "Female", "HR"),
        (5, "Male", "HR"),
        (6, "Female", "Finance"),
    ]
    response = client.get("/get_statistics?stat=gender_distribution_per_industry")
    
    assert response.status_code == 200
    assert response.json() == [
        {"industry": "Finance", "gender": "Female", "gender_count": 1, "total_employees": 1, "percentage": 100.0},
        {"industry": "HR", "gender": "Female", "gender_count": 1, "total_employees": 3, "percentage": 33.33333333333333},
        {"industry": "HR", "gender": "Male", "gender_count": 2, "total_employees": 3, "percentage": 66.66666666666666},
        {"industry": "IT", "gender": "Female", "gender_count": 1, "total_employees": 2, "percentage": 50.0},
        {"industry": "IT", "gender": "Male", "gender_count": 1, "total_employees": 2, "percentage": 50.0},
    ]


def test_percentage_above_threshold(mock_db_session):
    """Test for /percentage_above_threshold endpoint."""
    mock_db_session.query.return_value.all.return_value = [
        (1, 60000, "IT"),
        (2, 70000, "IT"),
        (3, 50000, "HR"),
        (4, 40000, "HR"),
        (5, 90000, "Finance"),
        (6, 80000, "Finance"),
    ]
    response = client.get("/get_statistics?stat=percentage_above_threshold&salary_threshold=65000")
    
    assert response.status_code == 200
    assert response.json() == [
        {"industry": "Finance", "total_employees": 2, "above_threshold": 2, "percentage_above_threshold": 100.0},
        {"industry": "HR", "total_employees": 2, "above_threshold": 0, "percentage_above_threshold": 0.0},
        {"industry": "IT", "total_employees": 2, "above_threshold": 1, "percentage_above_threshold": 50.0},
    ]
