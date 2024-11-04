from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, event
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError

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
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    creator = relationship("User", back_populates="surveys")
    votes = relationship("Vote", back_populates="survey")

class SurveyOption(Base):
    __tablename__ = 'survey_options'

    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'), nullable=False)
    text = Column(String, nullable=False)

    survey = relationship("Survey", back_populates="options")
    votes = relationship("Vote", back_populates="option")

class Vote(Base):
    __tablename__ = 'votes'

    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'), nullable=False)
    option_id = Column(Integer, ForeignKey('survey_options.id'), nullable=False)
    ip_address = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    survey = relationship("Survey", back_populates="votes")
    option = relationship("SurveyOption", back_populates="votes")

# Create the database
engine = create_engine('sqlite:///survey.db')

# Event listeners to enforce the 2-5 options rule
@event.listens_for(SurveyOption, 'after_insert')
@event.listens_for(SurveyOption, 'after_delete')
def check_survey_options(mapper, connection, target):
    survey_id = target.survey_id
    stmt = f"SELECT COUNT(*) FROM survey_options WHERE survey_id = {survey_id}"
    count = connection.execute(stmt).scalar()
    if count < 2 or count > 5:
        raise IntegrityError("A survey must have between 2 and 5 options", None, None)

Base.metadata.create_all(engine)
