import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from marshmallow import Schema, fields, validate, ValidationError
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customer_survey.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('register'))
        new_user = User(email=email, password_hash=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('You have been logged in!')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password')
    return render_template('login.html', title='Login')

@app.route('/create_survey', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        options = request.form.get('options').split('\n')
        
        new_survey = Survey(title=title, description=description, creator_id=current_user.id)
        db.session.add(new_survey)
        for option_text in options:
            option = SurveyOption(text=option_text.strip(), survey=new_survey)
            db.session.add(option)
        db.session.commit()
        flash('Your survey has been created!')
        return redirect(url_for('index'))
    return render_template('create_survey.html', title='Create Survey')

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
    if request.method == 'POST':
        option_id = request.form.get('option')
        email = request.form.get('email') or None
        comment = request.form.get('comment')
        
        option = SurveyOption.query.get(option_id)
        if not option or option.survey_id != survey.id:
            flash('Invalid option selected')
            return redirect(url_for('survey', survey_id=survey_id))
        
        feedback = Feedback(survey_id=survey_id, option_id=option_id, user_email=email, comment=comment)
        db.session.add(feedback)
        db.session.commit()
        flash('Thank you for your feedback!')
        return redirect(url_for('index'))
    
    return render_template('survey.html', title=survey.title, survey=survey)

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
