from app import User, Survey, SurveyOption, Feedback, bcrypt, db

def test_survey_submission(client, init_database):
    # Log in and create a survey
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)

    # Create a survey (reuse code or setup survey directly in the database)
    survey = Survey(
        title='Service Feedback',
        description='Let us know your thoughts.',
        creator_id=1
    )
    option1 = SurveyOption(text='Excellent', survey=survey)
    option2 = SurveyOption(text='Good', survey=survey)
    db.session.add_all([survey, option1, option2])
    db.session.commit()

    # Log out to simulate a different user
    client.get('/logout', follow_redirects=True)

    # Access the survey page
    response = client.get(f'/survey/{survey.id}')
    assert response.status_code == 200

    # Submit feedback
    response = client.post(f'/survey/{survey.id}', data={
        'option': option1.id,
        'email': 'feedbackuser@example.com',
        'comment': 'Great service!'
    }, follow_redirects=True)
    assert b'Thank you for your feedback!' in response.data
