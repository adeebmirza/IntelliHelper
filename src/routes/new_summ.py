from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import jsonify
from src.News_Summarizer.process import summarizeTextP
from src.News_Summarizer.model_load import prediction_model
text_summarzize = Blueprint('text', __name__)

@text_summarzize.route('/news_summarize', methods=['GET'])
def index():
    return render_template("summarize.html")

@text_summarzize.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Use prediction_model as the model argument
    summary = summarizeTextP(text, prediction_model)
    return jsonify({"summary": summary})

