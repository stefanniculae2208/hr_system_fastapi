Dependencies:

        python
        postgresql


General:

        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        alembic init alembic

        Setup .env:

                Must replace user_name, user_password and db_name in the env file with one from your postgres.

                # Run from Docker:
                POSTGRES_USER=<user_name>
                POSTGRES_PASSWORD=<user_password>
                POSTGRES_DB=<db_name>
                DATABASE_URL=postgresql://<user_name>:<user_password>@dbfastapi:5432/<db_name> OR

                # Run from App:
                POSTGRES_USER=<user_name>
                POSTGRES_PASSWORD=<user_password>
                POSTGRES_DB=<db_name> 
                DATABASE_URL=postgresql://<user_name>:<user_password>@localhost/<db_name>


TEST:
        
        pytest


APP:

        alembic upgrade head
        alembic revision --autogenerate -m ""
        alembic upgrade head
        pip install -r requirements.txt
        uvicorn main:app --reload


DOCKER:

        # Disable SELinux if needed. It was stopping me from running this on my PC.
        sudo setenforce 0
        docker-compose build
        docker-compose up
        sudo docker exec -it fastapi_app /bin/bash
        alembic upgrade head
        alembic revision --autogenerate -m ""
        alembic upgrade head
        exit
        curl -X POST "http://127.0.0.1:8000/upload_employees/" \
        -H "accept: application/json" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@data/MOCK_DATA.json"
        

CURL:

    curl -X GET "http://localhost:8000/employees/"

    curl -X GET "http://localhost:8000/employees/1"

    curl -X DELETE "http://localhost:8000/employees/1"

    curl -X PUT "http://localhost:8000/employees/2"      -H "Content-Type: application/json"      -d '{
            "salary": 80000,
            "years_of_experience": 16
            }'

    curl -X POST "http://localhost:8000/employees/"      -H "Content-Type: application/json"      -d '{
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "gender": "F",
            "date_of_birth": "1980-01-01",
            "industry": "IT",
            "salary": 70000,
            "years_of_experience": 15
            }'

    curl -X GET "http://localhost:8000/employees_filtered/?page=2&page_size=5" -H "accept: application/json"

    curl -X GET "http://localhost:8000/employees_filtered/?first_name=John" -H "accept: application/json"

    curl -X GET "http://127.0.0.1:8000/api/hr_app/get_statistics?stat=average_age_by_industry" -H "accept: application/json"

    curl -X GET "http://127.0.0.1:8000/api/hr_app/get_statistics?stat=average_salary_by_industry" -H "accept: application/json"

    curl -X GET "http://127.0.0.1:8000/api/hr_app/get_statistics?stat=average_salary_by_experience" -H "accept: application/json"

    curl -X GET "http://127.0.0.1:8000/api/hr_app/get_statistics?stat=gender_distribution_per_industry" -H "accept: application/json"

    curl -X GET "http://127.0.0.1:8000/api/hr_app/get_statistics?stat=percentage_above_threshold&salary_threshold=50000" -H "accept: application/json"

    curl -X POST "http://127.0.0.1:8000/upload_employees/" \
    -H "accept: application/json" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@data/MOCK_DATA.json"
