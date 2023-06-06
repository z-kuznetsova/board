from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

engine = create_engine('postgresql://root:1@postgres/board')

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable= True)
    registration_date = Column(DateTime(), default=datetime.now)
    

class Board(Base):
    __tablename__ = "boards"
    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable= False)
    date = Column(DateTime(), default=datetime.now)
    user_id = Column(ForeignKey('users.id'))