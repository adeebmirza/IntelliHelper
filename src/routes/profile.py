from flask import flash,Blueprint, render_template, redirect, url_for, session, request, current_app
from src.profile.verification_email import  send_forget
from src.profile.forget import generate_reset_token, verify_reset_token
from src.profile.form import ResetForm
from src.profile.pic_profile import handle_profile_pic_upload,allowed_file
from src.database import get_user_by_id, users_collection,handle_password_update,update_user_info
from passlib.hash import argon2
from argon2 import PasswordHasher

profile_bp = Blueprint('profile', __name__)
argon2 = PasswordHasher()

# profile.py


@profile_bp.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user']['_id']
    user_data = get_user_by_id(user_id)
    
    if user_data is None:
        return "User not found", 404

    display_data = {k: v for k, v in user_data.items() if k not in ['_id', 'password']}
    
    return render_template('profile.html', display_data=display_data)

from bson import ObjectId  # Import ObjectId if user_id is of type ObjectId in MongoDB

@profile_bp.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user']['_id']
    user_data = get_user_by_id(user_id)
    
    if user_data is None:
        return "User not found", 404

    if request.method == 'POST':
        update_data = {
            'name': request.form.get('name'),
            'dob': request.form.get('dob'),
            'gender': request.form.get('gender')
        }

        update_data.update(handle_password_update(request.form.get('password')))
        update_data.update(handle_profile_pic_upload(request.files.get('profile_pic')))

        update_user_info(user_id, update_data)
        flash('Your profile has been updated successfully!')
        return redirect(url_for('profile.profile'))

    return render_template('update_profile.html', user_data=user_data)



@profile_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = users_collection.find_one({'email': email})
        if user:
            secret_key = current_app.config['SECRET_KEY']
            token = generate_reset_token(email, secret_key)
            # Send the reset email with token
            send_forget(email, token)
            print("Email sent",token)
            flash('An email has been sent to reset your password.')
        else:
            flash('No account found with that email address.', 'danger')
        return redirect(url_for('profile.forgot_password'))
    return render_template('forgot_password.html')

@profile_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    secret_key = current_app.config['SECRET_KEY']
    email = verify_reset_token(token, secret_key)
    if not email:
        return 'The reset link is invalid or has expired.'

    form = ResetForm()
    if form.validate_on_submit():
        hashed_password = argon2.hash(form.password.data)
        users_collection.update_one({'email': email}, {'$set': {'password': hashed_password}})
        flash('Your password has been updated successfully!')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', form=form)