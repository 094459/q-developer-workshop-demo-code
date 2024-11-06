# conftest.py

import pytest
from app import app as flask_app, db
from app import User, Survey, SurveyOption, Feedback, bcrypt

@pytest.fixture
def app():
    # Configure the app for testing
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SECRET_KEY'] = 'test-secret-key' 
    flask_app.config['RATELIMIT_DEFAULT'] = ["1000 per day", "500 per hour"]
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    # Create a test user
    hashed_password = bcrypt.generate_password_hash('Password123!').decode('utf-8')
    user = User(email='test@example.com', password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()

    yield db  # this is where the testing happens!

    db.session.remove()
    db.drop_all()
