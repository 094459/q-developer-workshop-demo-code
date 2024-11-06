def test_login_logout(client, init_database):
    # Test login page access
    response = client.get('/login')
    assert response.status_code == 200

    # Test successful login
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'Password123!'
    }, follow_redirects=True)
    assert b'Home' in response.data  # Assuming 'Home' is in the index page

    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert b'You have been logged out.' in response.data

    # Test login with incorrect password
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'WrongPassword!'
    }, follow_redirects=True)
    assert b'Login unsuccessful. Please check email and password' in response.data
