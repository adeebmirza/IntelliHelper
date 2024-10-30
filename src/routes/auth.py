from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src.profile.form import SignupForm, LoginForm
from src.database import create_user, find_user
from passlib.hash import argon2
from argon2 import PasswordHasher
import pyotp
from src.profile.verification_email import send
import datetime
from argon2.exceptions import VerifyMismatchError
auth_bp = Blueprint('auth', __name__)

argon2 = PasswordHasher()
otp_secrets = {}


@auth_bp.route('/', methods=['GET'])
def Home():
    return render_template('index.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if find_user({'username': form.username.data}) and find_user({'email': form.email.data}):
            flash('User already exists', 'error')
        else:
            otp_secret = pyotp.random_base32()  # Generate secret key
            totp = pyotp.TOTP(otp_secret)
            otp = totp.now()  # Generate OTP based on the secret key
            send(form.email.data, otp)  # Send OTP via email

            otp_secrets[form.email.data] = {
                'otp_secret': otp_secret,
                'user_data': {
                    'name': form.name.data,
                    'username': form.username.data,
                    'email': form.email.data,
                    'gender' : form.gender.data,
                    'dob' : form.dob.data,
                    'password': argon2.hash(form.password.data)
                }
            }
            return redirect(url_for('auth.verify_otp', email=form.email.data))
    return render_template('signup.html', form=form)



@auth_bp.route('/verify_otp/<email>', methods=['GET', 'POST'])
def verify_otp(email):
    otp_data = otp_secrets.get(email)
    

    if request.method == 'POST' and otp_data: 
        # Using default interval (30 seconds) and increase valid window to 10 for 5 minutes
        totp = pyotp.TOTP(otp_data['otp_secret'])
        
        if totp.verify(request.form['otp'], valid_window=10):  # Verify OTP with a 5-minute window
            create_user(otp_data['user_data'])
            otp_secrets.pop(email, None)  # Clean up after successful signup
            flash('OTP verified! Signup complete.', 'success')
            return redirect(url_for('auth.login'))
        flash('Invalid or expired OTP.', 'error')
    
    return render_template('verify_otp.html')




@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if user := session.get('user'):
        return redirect(url_for('profile.profile'))
    if form.validate_on_submit():
        login_input = form.username.data or form.email.data
        password = form.password.data

        user = find_user(login_input)
        
        if not user:
            flash('Username or email not found', 'error')
            return render_template('login.html', form=form)
        
        try:
            if argon2.verify(user['password'], password):
                user['_id'] = str(user['_id'])  # Convert ObjectId to string for session storage
                session['user'] = user
                return redirect(url_for('auth.Home'))
            else:
                flash('Invalid password', 'error')
        except VerifyMismatchError:
            flash('Invalid password', 'error')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('auth.Home'))
