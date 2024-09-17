from flask import flash,Blueprint, render_template, redirect, url_for, session, request, current_app
from src.profile.verification_email import  send_forget
from src.profile.forget import generate_reset_token, verify_reset_token
from src.profile.form import ResetForm
from src.database import get_user_by_id, users_collection
from passlib.hash import argon2
from argon2 import PasswordHasher

profile_bp = Blueprint('profile', __name__)
argon2 = PasswordHasher()

@profile_bp.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']['_id']
    user_data = get_user_by_id(user_id)
    
    if user_data is None:
        return "User not found", 404
    
    # Convert ObjectId to string for safety
    user_data['_id'] = str(user_data['_id'])
    
    return render_template('profile.html', name=user_data['name'], email=user_data['email'])


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