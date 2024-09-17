from flask import Blueprint, render_template, request
from src.ATS.resume_score import parse_resume, calculate_ats_score

ats_bp = Blueprint('ats', __name__)

@ats_bp.route('/resume_score', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        resume = request.files['resume']
        job_description = request.form['job_description']
        resume_text = parse_resume(resume)
        ats_score = calculate_ats_score(resume_text, job_description)
        
        return render_template('resume.html', score=ats_score)
    
    return render_template('resume.html', score=None)