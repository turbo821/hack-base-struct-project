from flask import Flask

from .config import settings
from .extensions import cors, db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    from .routes.health import router as health_router

    app.register_blueprint(health_router, url_prefix="/api")

    return app
