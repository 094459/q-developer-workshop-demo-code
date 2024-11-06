def test_create_survey(client, init_database):
    # Log in first
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)

    # Access the create survey page
    response = client.get('/create_survey')
    assert response.status_code == 200

    # Create a new survey
    response = client.post('/create_survey', data={
        'title': 'Customer Satisfaction',
        'description': 'Please rate our service.',
        'options-0': 'Very Satisfied',
        'options-1': 'Satisfied',
        'options-2': 'Neutral',
        'options-3': 'Dissatisfied',
        'options-4': 'Very Dissatisfied'
    }, follow_redirects=True)
    assert b'Your survey has been created!' in response.data
