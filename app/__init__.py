import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.entrepreneur import entrepreneur_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(entrepreneur_bp, url_prefix='/empresario')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Global Jinja context variables
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'Vila Nexus',
            'city_name': 'Vila dos Cabanos - Barcarena/PA',
            'neighborhoods': [
                'Vila dos Cabanos',
                'Novo Paraíso',
                'Praia do Caripi',
                'Centro Barcarena',
                'Vila do Conde',
                'Distrito Industrial',
                'São Francisco',
                'Laranjal'
            ]
        }

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
