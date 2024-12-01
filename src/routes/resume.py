from flask import Blueprint, redirect, url_for, session, render_template, request
from src.ATS.resume_score import parse_resume, calculate_ats_score
from src.database import get_user_by_id

ats_bp = Blueprint('ats', __name__)

@ats_bp.route('/resume_score', methods=['GET', 'POST'])
def index():
    # Fetch user data for profile picture display, whether GET or POST
    user = session.get('user')
    if user:
        user_id = user['_id']
        user_data = get_user_by_id(user_id)

        if user_data is None:
            return "User not found", 404

        display_data = {'profile_pic': user_data.get('profile_pic')}
    else:
        # Use default data if user is not in session
        display_data = {'profile_pic': 'default_profile_pic.jpg'}
    
    if request.method == 'POST':
        resume = request.files['resume']
        job_description = request.form['job_description']
        resume_text = parse_resume(resume)
        ats_score = calculate_ats_score(resume_text, job_description)
        
        return render_template('resume.html', score=ats_score, display_data=display_data)
    
    # For GET requests, no ATS score is initially shown
    return render_template('resume.html', score=None, display_data=display_data)
