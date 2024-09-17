'''
# make sure to download python -m spacy download en_core_web_sm
from src.profile.verification_email import send, send_forget
from flask import Flask, flash, render_template, request, redirect, url_for,session
from src.profile.form import SignupForm, LoginForm, ResetForm
from src.ATS.resume_score import parse_resume, calculate_ats_score
from src.database import create_user, find_user, get_user_by_id, users_collection
from passlib.hash import argon2
from src.database import users_collection
from argon2 import PasswordHasher
import pyotp
from src.profile.forget import generate_reset_token, verify_reset_token
argon2 = PasswordHasher()
app = Flask(__name__)

app.config['SECRET_KEY'] = 'a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef12345678'

otp_secrets = {}





if __name__ == '__main__':
    app.run(debug=True)
'''

from flask import Flask
from src.routes.auth import auth_bp
from src.routes.profile import profile_bp
from src.routes.resume import ats_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef12345678'

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp)
app.register_blueprint(ats_bp)

if __name__ == '__main__':
    app.run(debug=True)
