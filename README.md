# Customer Feedback App

## Overview
The Customer Feedback App is a Flask-based web application that allows businesses to create surveys, collect customer feedback, and analyze the results. It provides a simple and efficient way for companies to gather and assess customer opinions.

## Features
- User registration and authentication
- Survey creation with multiple choice options
- Survey submission for customers
- Results visualization for survey creators
- CSV export of survey results

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/xxxx/customer-feedback-app.git
   cd customer-feedback-app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   flask db upgrade
   ```

5. Run the application:
   ```
   flask run
   ```

The application will be available at `http://localhost:5000`.

## Usage

1. Register a new account or log in to an existing one.
2. Create a new survey by clicking on "Create Survey" and filling out the form.
3. Share the survey link with your customers.
4. View survey results by clicking on "View Results" for a specific survey.
5. Export survey results to CSV if needed.

For more detailed instructions, please refer to the [User Guide](USER_GUIDE.md).

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.