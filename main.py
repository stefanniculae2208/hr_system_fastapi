from src import models, database, utils, statistics
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from typing import List, Optional
import json

app = FastAPI()

# READ SINGLE
@app.get("/employees/{employee_id}", response_model=models.EmployeeBase)
def get_employee(employee_id: int, db: Session = Depends(database.get_db)):
    employee_db = db.query(models.EmployeeDb).filter(models.EmployeeDb.id == employee_id).first()
    if not employee_db:
        raise HTTPException(status_code=404, detail="Employee not found") 
    employee_pyd = models.EmployeeBase(
        id=employee_db.id,
        first_name=employee_db.first_name,
        last_name=employee_db.last_name,
        email=employee_db.email,
        gender=employee_db.gender,
        date_of_birth=employee_db.date_of_birth,
        industry=employee_db.industry,
        salary=employee_db.salary,
        years_of_experience=employee_db.years_of_experience,
    )
    return employee_pyd

# CREATE
@app.post("/employees/")
def create_item(employee_pyd: models.EmployeeBase, db: Session = Depends(database.get_db)):
    try:
        employee_db = models.EmployeeDb(
            first_name=employee_pyd.first_name,
            last_name=employee_pyd.last_name,
            email=employee_pyd.email,
            gender=employee_pyd.gender,
            date_of_birth=employee_pyd.date_of_birth,
            industry=employee_pyd.industry,
            salary=employee_pyd.salary,
            years_of_experience=employee_pyd.years_of_experience,
        )
        db.add(employee_db)
        db.commit()
        db.refresh(employee_db)
        return {"message": "Employee created successfully"}

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integrity Error: {e}",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {e}",
        )


# DELETE
@app.delete("/employees/{employee_id}")
def delete_item(employee_id: int, db: Session = Depends(database.get_db)):
    item = db.query(models.EmployeeDb).filter(models.EmployeeDb.id == employee_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Employee deleted successfully"}


# UPDATE
@app.put("/employees/{employee_id}", response_model=models.EmployeeBase)
def update_item(employee_id: int, updated_item: models.EmployeeUpdate, db: Session = Depends(database.get_db)):
    employee_db = db.query(models.EmployeeDb).filter(models.EmployeeDb.id == employee_id).first()
    if not employee_db:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in updated_item.model_dump().items():
        if key != "id" and value is not None:
            setattr(employee_db, key, value)
    db.commit()
    db.refresh(employee_db)
    return models.EmployeeBase(
        id=employee_db.id,
        first_name=employee_db.first_name,
        last_name=employee_db.last_name,
        email=employee_db.email,
        gender=employee_db.gender,
        date_of_birth=employee_db.date_of_birth,
        industry=employee_db.industry,
        salary=employee_db.salary,
        years_of_experience=employee_db.years_of_experience,
    )


# READ ALL
@app.get("/employees/", response_model=list[models.EmployeeBase])
def get_items(db: Session = Depends(database.get_db)):
    list_employee_db = db.query(models.EmployeeDb).all()
    list_employee_pyd = [
        models.EmployeeBase(
            id=employee_db.id,
            first_name=employee_db.first_name,
            last_name=employee_db.last_name,
            email=employee_db.email,
            gender=employee_db.gender,
            date_of_birth=employee_db.date_of_birth,
            industry=employee_db.industry,
            salary=employee_db.salary,
            years_of_experience=employee_db.years_of_experience,
        )
        for employee_db in list_employee_db
    ]
    return list_employee_pyd


# READ ALL FILTERED
@app.get("/employees_filtered/", response_model=list[models.EmployeeBase])
def get_items(
    params: models.EmployeeQueryParams = Depends(),
    db: Session = Depends(database.get_db),
):
    query = db.query(models.EmployeeDb)

    filters = {
        "first_name": lambda value: models.EmployeeDb.first_name.ilike(f"%{value}%"),
        "last_name": lambda value: models.EmployeeDb.last_name.ilike(f"%{value}%"),
        "email": lambda value: models.EmployeeDb.email.ilike(f"%{value}%"),
        "gender": lambda value: models.EmployeeDb.gender == value,
        "industry": lambda value: models.EmployeeDb.industry.ilike(f"%{value}%"),
        "min_salary": lambda value: models.EmployeeDb.salary >= value,
        "max_salary": lambda value: models.EmployeeDb.salary <= value,
        "min_years_of_experience": lambda value: models.EmployeeDb.years_of_experience >= value,
        "max_years_of_experience": lambda value: models.EmployeeDb.years_of_experience <= value,
        "date_of_birth_before": lambda value: models.EmployeeDb.date_of_birth <= value,
        "date_of_birth_after": lambda value: models.EmployeeDb.date_of_birth >= value,
    }
    for param, filter_fn in filters.items():
        value = getattr(params, param, None)
        if value is not None:
            query = query.filter(filter_fn(value))

    try:
        sort_column = getattr(models.EmployeeDb, params.sort_by, None)
        if sort_column:
            query = query.order_by(sort_column.desc() if params.sort_order.lower() == "desc" else sort_column.asc())
    except AttributeError:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by column: {params.sort_by}")

    if params.page and params.page_size:
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)

    list_employee_db = query.all()
    list_employee_pyd = [
        models.EmployeeBase(
            id=employee_db.id,
            first_name=employee_db.first_name,
            last_name=employee_db.last_name,
            email=employee_db.email,
            gender=employee_db.gender,
            date_of_birth=employee_db.date_of_birth,
            industry=employee_db.industry,
            salary=employee_db.salary,
            years_of_experience=employee_db.years_of_experience,
        )
        for employee_db in list_employee_db
    ]
    return list_employee_pyd


# STATISTICS
@app.get("/get_statistics")
def get_statistics(
    stat: str = Query(..., description="Statistic type to calculate"),
    salary_threshold: float = Query(None, description="Salary threshold (only for percentage_above_threshold)"),
    db: Session = Depends(database.get_db)
):
    # Mapping of stat types to functions
    function_map = {
        "average_age_by_industry": lambda: statistics.average_age_by_industry(db),
        "average_salary_by_industry": lambda: statistics.average_salary_by_industry(db),
        "average_salary_by_experience": lambda: statistics.average_salary_by_experience(db),
        "gender_distribution_per_industry": lambda: statistics.gender_distribution_per_industry(db),
        "percentage_above_threshold": lambda: statistics.percentage_above_threshold(salary_threshold=salary_threshold, db=db),
    }

    # Validate the stat parameter
    if stat not in function_map:
        raise HTTPException(status_code=400, detail=f"Invalid 'stat' value: {stat}")

    # Call the appropriate function
    try:
        return function_map[stat]()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# UPLOAD JSON TO DATABASE
@app.post("/upload_employees/")
def upload_employees(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    try:
        content = file.file.read()
        employees = json.loads(content)

        max_id_in_file = 0
        for employee_data in employees:
            try:
                employee_data['date_of_birth'] = datetime.strptime(employee_data['date_of_birth'], "%d/%m/%Y").date()
                #  If the added json file contains an ID column then the database autoincrement needs to be
                # manually set to the highest value of ID in order to avoid ID overlap (since it's the unique key).
                if 'id' in employee_data:
                    max_id_in_file = max(max_id_in_file, employee_data['id'])
                new_employee = models.EmployeeDb(**employee_data)
                db.add(new_employee)          
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error parsing employee data: {str(e)}")
        
        db.commit()
        if max_id_in_file > 0:
            db.execute(text(f"SELECT setval(pg_get_serial_sequence('employees', 'id'), {max_id_in_file}, true)")) 
        return {"status": "success", "message": "Employees added successfully"}  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
