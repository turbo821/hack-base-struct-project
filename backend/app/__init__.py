from flask import Flask
from .config import Config
from .extensions import db, migrate, cors
from .models import Message

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    cors.init_app(app)

    from .routes.health import bp as health_bp
    from .routes.hello import bp as hello_bp
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(hello_bp, url_prefix="/api")

    return app