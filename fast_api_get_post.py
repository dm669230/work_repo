
from os import path
from fastapi import FastAPI, Query, Depends
import uvicorn
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DB_URL = "mysql://root:mysql@localhost/new_schema"

engine = create_engine(SQLALCHEMY_DB_URL)
SessionLocal = sessionmaker(autocommit = False, bind = engine)
Base = declarative_base()

class Student_user(Base):
    __tablename__="student_list"
    name = Column("std_name",String(50))
    age = Column("std_age", Integer,primery_key = True)
    year = Column("std_year",String(100))


app=FastAPI()
def get_db():
    db= SessionLocal()
    try:
        yield db 
    finally:
        db.close()

Base.metadata.create_all(bind = engine)
app = FastAPI()

app=FastAPI()
students = {
    1 : {
        'name':'rohan',
        'age': 17,
         'class':'year 13'
    }
}
class Student(BaseModel):
    name: str
    age: int
    year: str

class UpdateStudents(BaseModel):
    name: Optional[str] = None
    age : Optional[int] = None
    year : Optional[str] = None

@app.get("/")
def index():
    return{'name':'first name'}

@app.get('/get-student/{student_id}')
def get_student(student_id: int):
    return students[student_id]

@app.get("/get-by-name/{student_id}") 
def get_student(*, student_id:int, name : Optional[str] = None, test : int):
    for student_id in students:
        if students[student_id]['name'] == name:
            return students[student_id]
        else:
            return "Data Not Found"
        

@app.post("/create-student/{student_id}")
def create_student(student_id : int,student : Student):
    if student_id in students:
        return {"Error" : "Student Already Exist"}
    
    students[student_id] = student
    return students[student_id]

@app.put("/update-student/{student_id}")
def update_student(student_id: int, student: UpdateStudents):
    if student_id not in students:
        return {"Error": "Student does not exist"}
    
    # students[student_id] = student

    
    if student.name != None:
        students[student_id].name = student.name

    if student.age != None:
        students[student_id].age = student.age

    if student.year != None:
        students[student_id].year = student.year

    return students[student_id]

@app.delete("/delete-student/{student_id}")
def delete_student(student_id : int):
    if student_id not in students:
        return {"Error": "student does not Exist"}
    del students[student_id]
    return {"message": "Student info deleted sucessfully"}

