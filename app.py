# make sure to download python -m spacy download en_core_web_sm

from flask import Flask, render_template, request, redirect, url_for
from src.profile.form import SignupForm, LoginForm
from src.ATS.resume_score import parse_resume, calculate_ats_score
from src.database import create_user, find_user
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key_here'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user_data = {
            'name': form.name.data,
            'username': form.username.data,
            'email': form.email.data,
            'password': form.password.data
        }
        create_user(user_data)
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.username.data or form.email.data
        password = form.password.data

        user = find_user(login_input)
       
        if user  and user['password'] == password:
            return 'Logged in successfully!'
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
        
        return render_template('index.html', score=ats_score)
    
    return render_template('index.html', score=None)
    
if __name__ == '__main__':
    app.run(debug=True)