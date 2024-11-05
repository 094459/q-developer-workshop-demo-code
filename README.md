# Customer Feedback Application

This is a Flask-based web application for creating and managing customer feedback surveys.

## Features

- User registration and login
- JWT authentication
- Survey creation (for authenticated users)
- Feedback submission
- Input validation
- Error handling and logging

## Setup

1. Install the required packages:
   ```
   pip install flask flask-sqlalchemy flask-bcrypt flask-jwt-extended marshmallow
   ```

2. Set up the database:
   ```
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

3. Run the application:
   ```
   python app.py
   ```

## API Endpoints

- POST /register: Register a new user
- POST /login: Login and receive a JWT token
- POST /surveys: Create a new survey (requires authentication)
- GET /surveys: Get all surveys for the authenticated user
- GET /surveys/<survey_id>: Get details of a specific survey
- POST /surveys/<survey_id>/feedback: Submit feedback for a survey

## Usage

1. Register a new user:
   ```
   curl -X POST -H "Content-Type: application/json" -d '{"email": "user@example.com", "password": "password123"}' http://localhost:5000/register
   ```

2. Login to get a JWT token:
   ```
   curl -X POST -H "Content-Type: application/json" -d '{"email": "user@example.com", "password": "password123"}' http://localhost:5000/login
   ```

3. Create a new survey (replace <JWT_TOKEN> with the token received from login):
   ```
   curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <JWT_TOKEN>" -d '{"title": "Customer Satisfaction", "description": "Rate our service", "options": ["Excellent", "Good", "Average", "Poor"]}' http://localhost:5000/surveys
   ```

4. Submit feedback for a survey:
   ```
   curl -X POST -H "Content-Type: application/json" -d '{"option_id": 1, "email": "customer@example.com", "comment": "Great service!"}' http://localhost:5000/surveys/1/feedback
   ```

## Security Considerations

- The JWT secret key should be changed in a production environment.
- HTTPS should be used in production to secure data transmission.
- Additional security measures like rate limiting should be implemented for production use.

### About this repo

This repo provides sample code to use as part of the [Amazon Q Developer workshop]()