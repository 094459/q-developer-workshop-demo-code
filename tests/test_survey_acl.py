# tests/test_survey.py

import pytest
from app import Survey, User, SurveyOption, Feedback, db, bcrypt

from flask import url_for

def test_survey_results_access_control(client, init_database):
    # Log in first
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Home' in response.data  # Adjust based on your actual response

    # Retrieve the logged-in user
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None  # Ensure the user exists

    # Create a new survey directly in the database with correct creator_id
    survey = Survey(
        title='Private Survey',
        description='Confidential survey.',
        creator_id=user.id  # Dynamically set to logged-in user's ID
    )
    option1 = SurveyOption(text='Option 1', survey=survey)
    option2 = SurveyOption(text='Option 2', survey=survey)
    db.session.add_all([survey, option1, option2])
    db.session.commit()

    # Attempt to access results while logged in as the creator
    response = client.get(f'/survey/{survey.id}/results')
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert b'Results - Private Survey' in response.data  # Adjust based on your actual response

    # Log out and try to access results
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out.' in response.data

    response = client.get(f'/survey/{survey.id}/results', follow_redirects=True)
    assert response.status_code == 200  # After following redirects, should be 200
    assert b'Please log in to access this page.' in response.data  # Adjust based on your flash message

    # Log in as another user
    hashed_password = bcrypt.generate_password_hash('Password123!').decode('utf-8')
    other_user = User(email='otheruser@example.com', password_hash=hashed_password)
    db.session.add(other_user)
    db.session.commit()
    response = client.post('/login', data={
        'email': 'otheruser@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Home' in response.data  # Adjust based on your actual response

    # Attempt to access the survey results as a different user
    response = client.get(f'/survey/{survey.id}/results', follow_redirects=True)
    assert response.status_code == 200  # After following redirects, should be 200
    assert b'You do not have permission to view these results' in response.data  # Adjust based on your flash message
