# make sure to download python -m spacy download en_core_web_sm
from datetime import timedelta
from flask import Flask
from src.routes.auth import auth_bp
from src.routes.profile import profile_bp
from src.routes.resume import ats_bp
from src.routes.todo import todo
from src.routes.news import news_bp
from src.routes.new_summ import text_summarzize
from src.routes.medical_bot import bot_bp
from src.routes.notes import notes
from flask_session import Session
from flask import Flask, session
from src.routes.about import about_bp

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem or another server-side option
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12) 
Session(app)

app.config['SECRET_KEY'] = 'a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef12345678'

@app.before_request
def make_session_permanent():
    session.permanent = True
# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp)
app.register_blueprint(ats_bp)
app.register_blueprint(todo)
app.register_blueprint(news_bp)
app.register_blueprint(text_summarzize)
app.register_blueprint(bot_bp)
app.register_blueprint(notes)
app.register_blueprint(about_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

