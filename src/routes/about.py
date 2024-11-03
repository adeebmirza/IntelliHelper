from flask import Blueprint, render_template,session, redirect, url_for
from src.database import get_user_by_id

about_bp = Blueprint('about',__name__)

@about_bp.route('/', methods=['GET'])
def Home():
    user = session.get('user')  # Get user data from session if it exists, otherwise None

    if user:
        user_id = user['_id']
        user_data = get_user_by_id(user_id)

        if user_data is None:
            return "User not found", 404

        display_data = {'profile_pic': user_data.get('profile_pic')}
    else:
        # Use default data if user is not in session
        display_data = {'profile_pic': 'default_profile_pic.jpg'}  # Replace with a path to a default image if desired

    return render_template('index.html', display_data=display_data)


@about_bp.route('/about')
def about():
    return render_template('about.html')