from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    surveys = relationship("Survey", back_populates="creator")

class Survey(Base):
    __tablename__ = 'surveys'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    creator = relationship("User", back_populates="surveys")

class SurveyOption(Base):
    __tablename__ = 'survey_options'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'), nullable=False)
    text = Column(String, nullable=False)
    survey = relationship("Survey", back_populates="options")
    feedbacks = relationship("Feedback", back_populates="selected_option")

class Feedback(Base):
    __tablename__ = 'feedbacks'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'), nullable=False)
    option_id = Column(Integer, ForeignKey('survey_options.id'), nullable=False)
    user_email = Column(String, nullable=False)
    comment = Column(String)
    created_at = Column(DateTime, server_default=func.now())

# Create the database
engine = create_engine('sqlite:///customer_survey.db')
Base.metadata.create_all(engine)