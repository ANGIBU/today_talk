from flask import Flask
from .check_nickname import check_nickname_blueprint
from .check_id import check_id_blueprint
from .check_email import check_email_blueprint

def register_blueprints(app: Flask):
    """
    Register API blueprints with the Flask app.
    """
    app.register_blueprint(check_nickname_blueprint)
    app.register_blueprint(check_id_blueprint)
    app.register_blueprint(check_email_blueprint)

def create_api_blueprints(app: Flask):
    """
    Alias for register_blueprints to maintain compatibility.
    """
    register_blueprints(app)
