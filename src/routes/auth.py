from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src.profile.form import SignupForm, LoginForm
from src.database import create_user, find_user
from passlib.hash import argon2
from argon2 import PasswordHasher
import pyotp
from src.profile.verification_email import send

auth_bp = Blueprint('auth', __name__)


argon2 = PasswordHasher()
otp_secrets = {}


@auth_bp.route('/',methods = ['GET'])
def Home():
    return render_template('index.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if find_user({'username': form.username.data} or {'email': form.email.data}):
            flash('User already exists', 'error')
        else:
            otp_secret = pyotp.random_base32()
            otp = pyotp.TOTP(otp_secret).now()
            send(form.email.data, otp)

            otp_secrets[form.email.data] = {
                'otp_secret': otp_secret,
                'user_data': {
                    'name': form.name.data,
                    'username': form.username.data,
                    'email': form.email.data,
                    'password': argon2.hash(form.password.data)
                }
            }
            return redirect(url_for('auth.verify_otp', email=form.email.data))
    return render_template('signup.html', form=form)

@auth_bp.route('/verify_otp/<email>', methods=['GET', 'POST'])
def verify_otp(email):
    otp_data = otp_secrets.get(email)
    if request.method == 'POST' and otp_data:
        if pyotp.TOTP(otp_data['otp_secret']).verify(request.form['otp']):
            create_user(otp_data['user_data'])
            otp_secrets.pop(email, None)
            flash('OTP verified! Signup complete.', 'success')
            return redirect(url_for('auth.login'))
        flash('Invalid or expired OTP.', 'error')
    return render_template('verify_otp.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.username.data or form.email.data
        password = form.password.data

        user = find_user(login_input)
       
        if user and argon2.verify(user['password'], password):
            user['_id'] = str(user['_id'])
            session['user'] = user
            return redirect(url_for('auth.Home'))
        return 'Invalid username or password'
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.Home'))