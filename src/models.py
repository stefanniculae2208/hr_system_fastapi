from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import date

Base = declarative_base()

class EmployeeDb(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True, nullable=True)
    gender = Column(String, nullable=True)  # can be null
    date_of_birth = Column(Date, nullable=True)
    industry = Column(String, nullable=True)
    salary = Column(Float, nullable=True)
    years_of_experience = Column(Integer, nullable=True)  # optional


class EmployeeBase(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    email: Optional[str]
    gender: Optional[str] = None
    date_of_birth: Optional[date]
    industry: Optional[str]
    salary: Optional[float]
    years_of_experience: Optional[int] = None


class EmployeeUpdate(EmployeeBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    

class EmployeeQueryParams(BaseModel):
    sort_by: Optional[str] = "id"  # Default sorting by ID
    sort_order: Optional[str] = "asc"  # Default ascending order
    page: Optional[int] = 1  # Default to the first page
    page_size: Optional[int] = 10  # Default page size
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    industry: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    min_years_of_experience: Optional[int] = None
    max_years_of_experience: Optional[int] = None
    date_of_birth_before: Optional[date] = None
    date_of_birth_after: Optional[date] = None

