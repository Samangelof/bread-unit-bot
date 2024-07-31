from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


Base = declarative_base()

class UserRequest(Base):
    __tablename__ = 'user_requests'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    user_id = Column(Integer)
    request_time = Column(DateTime, default=datetime.utcnow)
    request_text = Column(Text)


engine = create_engine('sqlite:///user_requests.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
