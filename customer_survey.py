from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

# Create a base class for declarative class definitions
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    surveys = relationship("Survey", back_populates="creator", cascade="all, delete-orphan")

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

class SurveyResponse(Base):
    __tablename__ = 'survey_responses'

    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'), nullable=False)
    option_id = Column(Integer, ForeignKey('survey_options.id'), nullable=False)
    respondent_email = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    survey = relationship("Survey", back_populates="responses")
    option = relationship("SurveyOption")

@event.listens_for(SurveyOption, 'after_insert')
@event.listens_for(SurveyOption, 'after_delete')
def check_survey_options(mapper, connection, target):
    survey_id = target.survey_id
    stmt = f"SELECT COUNT(*) FROM survey_options WHERE survey_id = {survey_id}"
    count = connection.execute(stmt).scalar()
    if count < 2 or count > 5:
        raise IntegrityError("A survey must have between 2 and 5 options", None, None)

# Function to create tables
def create_tables(engine):
    Base.metadata.create_all(engine)

# If you want to create the tables, uncomment and use the following lines:
engine = create_engine('sqlite:///customer_survey.db', echo=True)
create_tables(engine)
