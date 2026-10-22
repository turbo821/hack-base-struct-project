import logging

from flask import Flask

from .config import settings
from .extensions import cors, db, migrate
from .logging_config import setup_logging, get_logger

logger = get_logger("main_init")

def create_app():
    setup_logging(name="backend")
    app = Flask(__name__)

    logger.info("Инициализация backend-приложения")

    logger.info("Инициализация .env-переменных")
    app.config.from_object(settings)
    logger.info(".env-переменные в порядке")

    # db.init_app(app)
    # migrate.init_app(app, db)
    # cors.init_app(app)

    from .routes.health import router as health_router

    app.register_blueprint(health_router, url_prefix="/api")

    # Flask создаёт свой логгер с дефолтным хендлером в stderr.
    # Если его не убрать — каждая запись уйдёт дважды: в наш файл И в stderr мимо хендлеров.
    app.logger.handlers.clear()
    app.logger.setLevel(logging.INFO)

    # werkzeug в dev-режиме тоже печатает access-логи своим хендлером → дубли.
    # В боте ровно так же глушили aiogram: logging.getLogger("aiogram").setLevel(WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    return app
