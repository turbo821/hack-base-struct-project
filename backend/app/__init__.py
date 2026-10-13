from flask import Flask
from .config import Config
from .extensions import db, migrate, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from .routes.health import bp as health_bp
    app.register_blueprint(health_bp, url_prefix="/api")

    return app