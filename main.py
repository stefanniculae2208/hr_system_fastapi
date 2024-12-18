from src import models, database, utils
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
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


# AGE BY INDUSTRY
@app.get("/average_age_by_industry", response_model=List[models.AvgAgeByIndustry])
def average_age_by_industry(db: Session = Depends(database.get_db)):
    list_employee_db = db.query(
        models.EmployeeDb.id,
        models.EmployeeDb.industry,
        models.EmployeeDb.date_of_birth
    ).all()
    df = pd.DataFrame(list_employee_db, columns=["id", "industry", "date_of_birth"])
    df['age'] = df['date_of_birth'].apply(utils.calculate_age)
    avg_age_by_industry = df.groupby('industry')['age'].mean().reset_index()
    avg_age_by_industry.rename(columns={'ag   # Query to fetch relevant dataate_of_birth,e': 'average_age'}, inplace=True)
    result = avg_age_by_industry.to_dict(orient="records")
    response = [models.AvgAgeByIndustry(**item) for item in result]
    return response


# SALARY BY INDUSTRY
@app.get("/average_salary_by_industry", response_model=List[models.AvgSalaryByIndustry])
def average_salary_by_industry(db: Session = Depends(database.get_db)):
    list_employee_db = db.query(
        models.EmployeeDb.id,
        models.EmployeeDb.industry,
        models.EmployeeDb.salary   # Query to fetch relevant dataate_of_birth,
    ).all()
    df = pd.DataFrame(list_employee_db, columns=["id", "industry", "salary"])
    avg_age_by_industry = df.groupby('industry')['salary'].mean().reset_index()
    avg_age_by_industry.rename(columns={'salary': 'average_salary'}, inplace=True)
    result = avg_age_by_industry.to_dict(orient="records")
    response = [models.AvgSalaryByIndustry(**item) for item in result]
    return response


# SALARY BY INDUSTRY
@app.get("/average_salary_by_experience", response_model=List[models.AvgSalaryByExperience])
def average_salary_by_experience(db: Session = Depends(database.get_db)):
    list_employee_db = db.query(
        models.EmployeeDb.id,
        models.EmployeeDb.years_of_experience,
        models.EmployeeDb.salary
    ).all()
    df = pd.DataFrame(list_employee_db, columns=["id", "years_of_experience", "salary"])
    df = df.dropna(subset=["years_of_experience"])
    avg_age_by_industry = df.groupby('years_of_experience')['salary'].mean().reset_index()
    avg_age_by_industry.rename(columns={'salary': 'average_salary'}, inplace=True)
    result = avg_age_by_industry.to_dict(orient="records")
    response = [models.AvgSalaryByExperience(**item) for item in result]
    return response


# READ ALL FILTERED
@app.get("/employees_filtered/", response_model=list[models.EmployeeBase])
def get_items(
    params: models.EmployeeQueryParams = Depends(),
    db: Session = Depends(database.get_db),
):
    query = db.query(models.EmployeeDb)
    if params.first_name:
        query = query.filter(models.EmployeeDb.first_name.ilike(f"%{params.first_name}%"))
    if params.last_name:
        query = query.filter(models.EmployeeDb.last_name.ilike(f"%{params.last_name}%"))
    if params.email:
        query = query.filter(models.EmployeeDb.email.ilike(f"%{params.email}%"))
    if params.gender:
        query = query.filter(models.EmployeeDb.gender == params.gender)
    if params.industry:
        query = query.filter(models.EmployeeDb.industry.ilike(f"%{params.industry}%"))
    if params.min_salary is not None:
        query = query.filter(models.EmployeeDb.salary >= params.min_salary)
    if params.max_salary is not None:
        query = query.filter(models.EmployeeDb.salary <= params.max_salary)
    if params.min_years_of_experience is not None:
        query = query.filter(models.EmployeeDb.years_of_experience >= params.min_years_of_experience)
    if params.max_years_of_experience is not None:
        query = query.filter(models.EmployeeDb.years_of_experience <= params.max_years_of_experience)
    if params.date_of_birth_before:
        query = query.filter(models.EmployeeDb.date_of_birth <= params.date_of_birth_before)
    if params.date_of_birth_after:
        query = query.filter(models.EmployeeDb.date_of_birth >= params.date_of_birth_after)

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


# GENDER DISTRIBUTION PER INDUSTRY
@app.get("/gender_distribution_per_industry", response_model=List[models.GenderDistribution])
def gender_distribution_per_industry(db: Session = Depends(database.get_db)):
    list_employee_db = db.query(
        models.EmployeeDb.id,
        models.EmployeeDb.gender,
        models.EmployeeDb.industry
    ).all()
    df = pd.DataFrame(list_employee_db, columns=["id", "gender", "industry"])
    total_by_industry = df.groupby("industry")["id"].count().reset_index().rename(columns={"id": "total_employees"})
    gender_distribution = df.groupby(["industry", "gender"])["id"].count().reset_index().rename(columns={"id": "gender_count"})
    merged_df = gender_distribution.merge(total_by_industry, on="industry")
    merged_df["percentage"] = (merged_df["gender_count"] / merged_df["total_employees"]) * 100
    result = merged_df.to_dict(orient="records")
    response = [models.GenderDistribution(**item) for item in result]
    return response


# PERCENTAGE EMPLOYEES ABOVE A THRESHOLD
@app.get("/percentage_above_threshold", response_model=List[models.PercentageAboveThreshold])
def percentage_above_threshold(
    salary_threshold: float = Query(..., description="Salary threshold to calculate the percentage"),
    db: Session = Depends(database.get_db)
):
    list_employee_db = db.query(
        models.EmployeeDb.id,
        models.EmployeeDb.salary,
        models.EmployeeDb.industry
    ).all()
    df = pd.DataFrame(list_employee_db, columns=["id", "salary", "industry"])
    total_by_industry = df.groupby("industry")["id"].count().reset_index().rename(columns={"id": "total_employees"})
    above_threshold = df[df["salary"] > salary_threshold].groupby("industry")["id"].count().reset_index().rename(columns={"id": "above_threshold"})
    merged_df = above_threshold.merge(total_by_industry, on="industry", how="right").fillna(0)
    merged_df["percentage_above_threshold"] = (merged_df["above_threshold"] / merged_df["total_employees"]) * 100
    result = merged_df.to_dict(orient="records")
    response = [models.PercentageAboveThreshold(**item) for item in result]
    return response


@app.post("/upload_employees/")
def upload_employees(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    try:
        # Read the file and parse JSON content
        content = file.file.read()
        employees = json.loads(content)
        
        # Convert and validate JSON data
        for employee_data in employees:
            try:
                # Convert date_of_birth from string to a date object
                employee_data['date_of_birth'] = datetime.strptime(employee_data['date_of_birth'], "%d/%m/%Y").date()
                
                # Create an EmployeeDb object
                new_employee = models.EmployeeDb(**employee_data)
                
                # Add to session
                db.add(new_employee)
            
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error parsing employee data: {str(e)}")
        
        # Commit the session
        db.commit()
        
        return {"status": "success", "message": "Employees added successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
