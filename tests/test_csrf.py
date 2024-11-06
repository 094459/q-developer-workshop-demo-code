def test_csrf_protection(client, app):
    # Enable CSRF protection for this test
    app.config['WTF_CSRF_ENABLED'] = True

    # Attempt to submit the login form without a CSRF token
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'Password123!'
    })
    assert b'The CSRF token is missing.' in response.data
