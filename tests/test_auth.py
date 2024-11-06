# test_auth.py

def test_register(client):
    response = client.get('/register')
    assert response.status_code == 200

    # Test successful registration
    response = client.post('/register', data={
        'email': 'newuser@example.com',
        'password': 'Password123!',
        'password2': 'Password123!'
    }, follow_redirects=True)
    assert b'Congratulations, you are now a registered user!' in response.data

    # Test registering with an existing email
    response = client.post('/register', data={
        'email': 'newuser@example.com',
        'password': 'Password123!',
        'password2': 'Password123!'
    }, follow_redirects=True)
    assert b'Email address already exists' in response.data
