from flask import Flask
from pathlib import Path

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-only-change-me"
    app.config["PROJECT_ROOT"] = Path(__file__).resolve().parent.parent
    from app.routes import bp
    app.register_blueprint(bp)
    return app
