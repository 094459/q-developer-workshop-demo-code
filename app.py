# SPDX-FileCopyrightText: 2024 Beachgeek Enterprises
# SPDX-License-Identifier: Apache-2.0

# Copyright 2024 Beachgeek Enterprises
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, make_response, request, jsonify, render_template, redirect, url_for, flash, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from marshmallow import Schema, fields, validate, ValidationError
from flask_migrate import Migrate
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, RadioField, FieldList
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, Optional
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bleach
import csv
import os
from waitress import serve
from io import BytesIO, StringIO
from flask import send_file
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customer_survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret_key')  # Use environment variable
app.config['SESSION_COOKIE_SECURE'] = False  # Ensure secure cookies in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = False
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['SESSION_TYPE'] = 'filesystem'

csrf = CSRFProtect(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=app.config.get('RATELIMIT_DEFAULT', ["200 per day", "50 per hour"])
)

# Set up logging
if not app.debug:
    file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    surveys = relationship("Survey", back_populates="creator")

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    creator = relationship("User", back_populates="surveys")
    options = relationship("SurveyOption", back_populates="survey")

class SurveyOption(db.Model):
    __tablename__ = 'survey_options'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'), nullable=False)
    text = Column(String, nullable=False)
    survey = relationship("Survey", back_populates="options")
    feedbacks = relationship("Feedback", back_populates="selected_option")

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('surveys.id'), nullable=False)
    option_id = Column(Integer, ForeignKey('survey_options.id'), nullable=False)
    user_email = Column(String, nullable=True)
    comment = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    selected_option = relationship("SurveyOption", back_populates="feedbacks")

# Input validation schemas
class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class SurveySchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str()
    options = fields.List(fields.Str(), validate=validate.Length(min=2))

class FeedbackSchema(Schema):
    option_id = fields.Int(required=True)
    email = fields.Email(required=True)
    comment = fields.Str()

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
               message='Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character')
    ])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class CreateSurveyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = StringField('Description', validators=[Length(max=500)])
    options = FieldList(StringField('Option', validators=[DataRequired(), Length(max=200)]), min_entries=2, max_entries=10)
    submit = SubmitField('Create Survey')

class SurveySubmissionForm(FlaskForm):
    option = RadioField('Option', coerce=int, validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    comment = TextAreaField('Comment', validators=[Length(max=500)])
    submit = SubmitField('Submit')

def get_yoda_wisdom():
    import random
    
    yoda_quotes = [
        "Do or do not. There is no try.",
        "Size matters not. Look at me. Judge me by my size, do you?",
        "Fear is the path to the dark side.",
        "Patience you must have, my young Padawan.",
        "Much to learn, you still have.",
        "In a dark place we find ourselves, and a little more knowledge lights our way."
    ]
    
    return random.choice(yoda_quotes)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()

    if app.config.get('WTF_CSRF_ENABLED', True):
        app.logger.info(f"CSRF Token: {form.csrf_token.current_token}")
    else:
        app.logger.info("CSRF Protection is disabled.")

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
        try:
            new_user = User(email=form.email.data, password_hash=bcrypt.generate_password_hash(form.password.data).decode('utf-8'))
            db.session.add(new_user)
            db.session.commit()
            app.logger.info(f'New user registered: {form.email.data}')
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error during user registration: {str(e)}')
            flash('An error occurred during registration. Please try again.')
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
#@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    #app.logger.info(f"CSRF Token: {form.csrf_token.current_token}")
    if app.config.get('WTF_CSRF_ENABLED', True):
        app.logger.info(f"CSRF Token: {form.csrf_token.current_token}")
    else:
        app.logger.info("CSRF Protection is disabled.")
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            
            # Validate and sanitize the 'next' parameter
            if next_page:
                if not is_safe_url(next_page):
                    app.logger.warning(f'Potentially malicious redirect attempt to: {next_page}')
                    abort(400)  # Bad Request
            else:
                next_page = url_for('index')
            
            return redirect(next_page)
        else:
            flash('Login unsuccessful. Please check email and password')
            app.logger.warning(f'Failed login attempt for email: {form.email.data}')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/create_survey', methods=['GET', 'POST'])
@login_required
def create_survey():
    form = CreateSurveyForm()
    if form.validate_on_submit():
        new_survey = Survey(
            title=bleach.clean(form.title.data),
            description=bleach.clean(form.description.data),
            creator_id=current_user.id
        )
        db.session.add(new_survey)
        for option in form.options.data:
            if option.strip():  # Only add non-empty options
                option = SurveyOption(text=bleach.clean(option.strip()), survey=new_survey)
                db.session.add(option)
        db.session.commit()
        flash('Your survey has been created!')
        return redirect(url_for('index'))
    return render_template('create_survey.html', title='Create Survey', form=form)

@app.route('/')
@app.route('/index')
def index():
    surveys = []
    if current_user.is_authenticated:
        surveys = Survey.query.filter_by(creator_id=current_user.id).all()
    return render_template('index.html', title='Home', surveys=surveys)

@app.route('/survey/<int:survey_id>', methods=['GET', 'POST'])
def survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    form = SurveySubmissionForm()
    form.option.choices = [(option.id, option.text) for option in survey.options]
    
    if form.validate_on_submit():
        option = SurveyOption.query.get(form.option.data)
        if not option or option.survey_id != survey.id:
            flash('Invalid option selected')
            return redirect(url_for('survey', survey_id=survey_id))
        
        feedback = Feedback(
            survey_id=survey_id,
            option_id=form.option.data,
            user_email=bleach.clean(form.email.data) if form.email.data else None,
            comment=bleach.clean(form.comment.data)
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Thank you for your feedback!')
        return redirect(url_for('index'))
    
    return render_template('survey.html', title=bleach.clean(survey.title), survey=survey, form=form)

@app.route('/survey/<int:survey_id>/results')
@login_required
def survey_results(survey_id):
    # Get the survey and verify the current user is the creator
    survey = Survey.query.get_or_404(survey_id)
    if survey.creator_id != current_user.id:
        flash('You do not have permission to view these results')
        return redirect(url_for('index'))
    
    # Get all feedback for this survey
    feedbacks = Feedback.query.filter_by(survey_id=survey_id).all()
    
    # Calculate results for each option
    results = {}
    total_responses = len(feedbacks)
    
    for option in survey.options:
        option_feedbacks = [f for f in feedbacks if f.option_id == option.id]
        count = len(option_feedbacks)
        percentage = (count / total_responses * 100) if total_responses > 0 else 0
        
        results[option.id] = {
            'text': option.text,
            'count': count,
            'percentage': round(percentage, 1),
            'comments': [f.comment for f in option_feedbacks if f.comment]
        }
    
    return render_template('survey_results.html',
                         title=f'Results - {survey.title}',
                         survey=survey,
                         results=results,
                         total_responses=total_responses)


@app.route('/survey/<int:survey_id>/export', methods=['GET'])
@login_required
def export_survey_results(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if survey.creator_id != current_user.id:
        flash('You do not have permission to export these results')
        return redirect(url_for('index'))

    include_email = request.args.get('include_email', 'false').lower() == 'true'
   
    feedbacks = Feedback.query.filter_by(survey_id=survey_id).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    header = ['Timestamp', 'Selected Option']
    if include_email:
        header.extend(['Email', 'Comment'])
    else:
        header.append('Comment')
    writer.writerow(header)
    
    # Write each feedback as a row
    for feedback in feedbacks:
        row = [
            feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            feedback.selected_option.text
        ]
        if include_email:
            row.extend([feedback.user_email or '', feedback.comment or ''])
        else:
            row.append(feedback.comment or '')
        writer.writerow(row)
    
    output.seek(0)
    
    filename = f"{survey.title}_results.csv"
    return send_file(BytesIO(output.getvalue().encode('utf-8')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=filename)

@app.route('/about')
def about():
    wisdom = get_yoda_wisdom()  # This function should be defined in your app.py
    return render_template('about.html', wisdom=wisdom)

@app.route('/logout')
@login_required
def logout():
    app.logger.info(f"User {current_user.id} logging out")
    logout_user()
    session.clear()  # Clear the entire session
    
    response = make_response(redirect(url_for('index')))
    
    if 'remember_token' in request.cookies:
        response.set_cookie('remember_token', 
                            value='',  # Clear the cookie value
                            expires=0,  # Make the cookie expire immediately
                            secure=False,  # Only send over HTTPS
                            httponly=True,  # Prevent client-side script access
                            samesite='Lax')  # Protect against CSRF
    
    app.logger.info("User logged out and session cleared")
    flash('You have been logged out.')
    return response


if __name__ == '__main__':
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; form-action 'self'"
        response.headers['Content-Security-Policy'] = csp
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    with app.app_context():
        db.create_all()
    # Get debug mode from environment variable, default to False
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Use a production-ready server when debug is False
    if debug_mode:
        app.run(debug=True)
    else:
        from waitress import serve
        serve(app, host='127.0.0.1', port=5000)
