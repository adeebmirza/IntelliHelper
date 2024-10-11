# make sure to download python -m spacy download en_core_web_sm

from flask import Flask
from src.routes.auth import auth_bp
from src.routes.profile import profile_bp
from src.routes.resume import ats_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef12345678'

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp)
app.register_blueprint(ats_bp)

if __name__ == '__main__':
    app.run(debug=True)
