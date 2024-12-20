import pandas as pd
from sqlalchemy.orm import Session
from . import models
from . import utils

def average_age_by_industry(db: Session):
    list_employee_db = db.query(
        models.EmployeeDb.id,
        models.EmployeeDb.industry,
        models.EmployeeDb.date_of_birth
    ).all()
    df = pd.DataFrame(list_employee_db, columns=["id", "industry", "date_of_birth"])
    df['age'] = df['date_of_birth'].apply(utils.calculate_age)
    avg_age_by_industry = df.groupby('industry')['age'].mean().reset_index()
    avg_age_by_industry.rename(columns={'age': 'average_age'}, inplace=True)
    return avg_age_by_industry.to_dict(orient="records")


def average_salary_by_industry(db: Session):
    list_employee_db = db.query(
        models.EmployeeDb.id,
        models.EmployeeDb.industry,
        models.EmployeeDb.salary
    ).all()
    df = pd.DataFrame(list_employee_db, columns=["id", "industry", "salary"])
    avg_salary_by_industry = df.groupby('industry')['salary'].mean().reset_index()
    avg_salary_by_industry.rename(columns={'salary': 'average_salary'}, inplace=True)
    return avg_salary_by_industry.to_dict(orient="records")


def average_salary_by_experience(db: Session):
    list_employee_db = db.query(
        models.EmployeeDb.id,
        models.EmployeeDb.years_of_experience,
        models.EmployeeDb.salary
    ).all()
    df = pd.DataFrame(list_employee_db, columns=["id", "years_of_experience", "salary"])
    df = df.dropna(subset=["years_of_experience"])
    avg_salary_by_experience = df.groupby('years_of_experience')['salary'].mean().reset_index()
    avg_salary_by_experience.rename(columns={'salary': 'average_salary'}, inplace=True)
    return avg_salary_by_experience.to_dict(orient="records")


def gender_distribution_per_industry(db: Session):
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
    return merged_df.to_dict(orient="records")


def percentage_above_threshold(salary_threshold: float, db: Session):
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
    return merged_df.to_dict(orient="records")
