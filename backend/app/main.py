from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .database import get_db, Base, engine, StudentDB
from .models import StudentCreate, Student


app = FastAPI(title="Student Form API")

Base.metadata.create_all(bind=engine)

origins = [
    "https://frontend.somyap.online",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/students", response_model=Student)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(StudentDB).filter(StudentDB.email == student.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_student = StudentDB(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    
    return db_student


#@app.get("/students", response_model=List[Student])
#def list_students(db: Session = Depends(get_db)):
#    students = db.query(StudentDB).all()
#    return students


@app.api_route("/students", methods=["GET", "HEAD"], response_model=List[Student])
def list_students(db: Session = Depends(get_db)):
    students = db.query(StudentDB).all()
    return students







@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for key, value in student.dict().items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(db_student)
    db.commit()
    return {"message": "Student deleted successfully"}
