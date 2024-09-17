from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length, EqualTo
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.logger import logger


#users = {}

class SignupForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=4, max=30)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Signup')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    submit = SubmitField('Login')

class ResetForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')