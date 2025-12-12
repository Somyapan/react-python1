from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    course: str
    age: int = Field(..., ge=0)


class Student(StudentCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True