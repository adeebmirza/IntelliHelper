from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
from src.Intelli_News.intelli_news_function import search_bing_news

news_bp = Blueprint('news', __name__)

@news_bp.route('/Intelli_news', methods=['GET'])
def index():
    # Check if a search query is provided in the URL
    query = request.args.get('query')
    try:
        if query:
            # Perform a search if a query parameter exists
            results = search_bing_news(query)
        else:
            # Use a general query to fetch the latest news
            results = search_bing_news("latest news")
    except requests.RequestException:
        # Handle internet connection issues
        return "Lost Internet Connection", 503  # 503 status for service unavailable

    return render_template('news.html', results=results)

@news_bp.route('/category/<category>')
def news_category(category):
    # Fetch news by category
    results = search_bing_news(category)
    return render_template('news.html', results=results)

