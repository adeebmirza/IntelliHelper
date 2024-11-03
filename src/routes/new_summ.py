from flask import Blueprint, render_template, request, redirect, url_for,session
from flask import jsonify
from src.News_Summarizer.process import summarizeTextP
from src.News_Summarizer.model_load import prediction_model
text_summarzize = Blueprint('text', __name__)

@text_summarzize.route('/news_summarize', methods=['GET'])
def index():
    from src.database import get_user_by_id
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user']['_id']
    user_data = get_user_by_id(user_id)
    
    if user_data is None:
        return "User not found", 404

    display_data = {'profile_pic': user_data.get('profile_pic')}
    return render_template("summarize.html", display_data=display_data)

@text_summarzize.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Use prediction_model as the model argument
    summary = summarizeTextP(text, prediction_model)
    return jsonify({"summary": summary})

