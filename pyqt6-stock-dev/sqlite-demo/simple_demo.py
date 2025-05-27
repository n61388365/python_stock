import sqlalchemy
engine = sqlalchemy.create_engine('sqlite:///sqlalchemy_example.db')


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = sqlalchemy.orm.declarative_base()


class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

# Create the table in the database
Base.metadata.create_all(engine)


from sqlalchemy.orm import sessionmaker

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

# Create a new student
new_student = Student(name='abhishek verma', age=20)

# Add the student to the session
session.add(new_student)

# Commit the session to the database
session.commit()

# Query all students
students = session.query(Student).all()

for student in students:
    print(f'ID: {student.id}, Name: {student.name}, Age: {student.age}')
