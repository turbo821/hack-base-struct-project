from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from database import init_db, create_tables, get_session, get_db_status
from backend.logger_config import get_logger
from config import Config
import os


# ============ ИНИЦИАЛИЗАЦИЯ ============
logger = get_logger(__name__)
app = Flask(__name__)

# НАСТРОЙКИ СЕССИИ ДЛЯ БРАУЗЕРА
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_DOMAIN=None,
    SESSION_COOKIE_PATH='/',
    PERMANENT_SESSION_LIFETIME=60 * 60 * 24 * 3
)


# ============ ИНИЦИАЛИЗАЦИЯ БД ============
if not os.environ.get('WERKZEUG_RUN_MAIN'):
    init_db(Config.DATABASE, echo=False)
    create_tables()
    logger.info(f"Статус БД: {get_db_status()}")

# ============ ПРОВЕРКА БД ПЕРЕД КАЖДЫМ ЗАПРОСОМ ============
@app.before_request
def ensure_db_initialized():
    try:
        get_session()
    except RuntimeError:
        logger.warning("⚠️ БД не инициализирована, выполняем инициализацию...")
        init_db(Config.DATABASE, echo=False)
        create_tables()
        logger.info("✅ БД инициализирована по запросу")


# ============ ЗАПУСК ============

if __name__ == '__main__':
    logger.info("🐍 Запуск Flask в режиме разработки")

    app.run(
        debug=False,
        threaded=True,
        host='0.0.0.0',
        port=5000
    )
