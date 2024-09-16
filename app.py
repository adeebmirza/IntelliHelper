# make sure to download python -m spacy download en_core_web_sm
from src.profile.verification_email import send
from flask import Flask, flash, render_template, request, redirect, url_for,session
from src.profile.form import SignupForm, LoginForm
from src.ATS.resume_score import parse_resume, calculate_ats_score
from src.database import create_user, find_user
from passlib.hash import argon2
from argon2 import PasswordHasher
import pyotp
from bson import ObjectId
argon2 = PasswordHasher()
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key_here'

otp_secrets = {}

@app.route('/',methods = ['GET'])
def Home():
    return render_template('index.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if find_user({'username': form.username.data}):
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
            return redirect(url_for('verify_otp', email=form.email.data))
    return render_template('signup.html', form=form)

@app.route('/verify_otp/<email>', methods=['GET', 'POST'])
def verify_otp(email):
    otp_data = otp_secrets.get(email)
    if request.method == 'POST' and otp_data:
        if pyotp.TOTP(otp_data['otp_secret']).verify(request.form['otp']):
            create_user(otp_data['user_data'])
            otp_secrets.pop(email, None)
            flash('OTP verified! Signup complete.', 'success')
            return redirect(url_for('login'))
        flash('Invalid or expired OTP.', 'error')
    return render_template('verify_otp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.username.data or form.email.data
        password = form.password.data

        user = find_user(login_input)
       
        if user and argon2.verify(user['password'], password):
            user['_id'] = str(user['_id'])
            session['user'] = user
            return redirect(url_for('Home'))
        return 'Invalid username or password'
    return render_template('login.html', form=form)

@app.route('/resume_score', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        resume = request.files['resume']
        job_description = request.form['job_description']
        
        # Parse resume and job description
        resume_text = parse_resume(resume)
        ats_score = calculate_ats_score(resume_text, job_description)
        
        return render_template('resume.html', score=ats_score)
    
    return render_template('resume.html', score=None)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('Home'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['_id']
    from src.database import users_collection
    
    # Convert ObjectId string back to ObjectId
    user_id = ObjectId(user_id)
    
    user_data = users_collection.find_one({'_id': user_id})
    
    if user_data is None:
        return "User not found", 404
    
    # Convert ObjectId to string for safety
    user_data['_id'] = str(user_data['_id'])
    
    return render_template('profile.html', name=user_data['name'], email=user_data['email'])

@app.route('/mail')
def send_mail():
    send('adeebmirzam3@gmail.com')
    return 'Mail sent successfully'

if __name__ == '__main__':
    app.run(debug=True)