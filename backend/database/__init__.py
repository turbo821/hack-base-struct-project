"""
Центральный модуль базы данных
Управляет подключением к БД, сессиями и предоставляет единый интерфейс
для всех моделей и менеджеров
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import sqlalchemy as sa
import pytz
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Базовый класс для всех моделей
Base = declarative_base()

# Глобальные переменные для подключения
_engine = None
_SessionLocal = None

# Московское время
MSK = pytz.timezone('Europe/Moscow')


def get_msk_now() -> datetime:
    """Возвращает текущее время в московском часовом поясе"""
    return datetime.now(MSK).replace(tzinfo=None)


def init_db(database_url: str, echo: bool = False) -> None:
    """
    Инициализация подключения к базе данных

    Args:
        database_url: URL подключения к БД (например, 'sqlite:///server.db')
        echo: Включить логирование SQL-запросов
    """
    global _engine, _SessionLocal

    if _engine is not None:
        logger.warning("База данных уже инициализирована. Повторная инициализация...")
        close_db()

    try:
        logger.info(f"Инициализация БД с URL: {database_url}")
        _engine = create_engine(
            database_url,
            echo=echo,
            pool_pre_ping=True,  # Проверка соединения перед использованием
            pool_recycle=3600,  # Пересоздание соединений каждый час
            connect_args={'check_same_thread': False} if 'sqlite' in database_url else {}
        )
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine
        )
        logger.info("✅ База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise


def close_db() -> None:
    """Закрытие подключения к базе данных"""
    global _engine, _SessionLocal
    if _engine:
        _engine.dispose()
        _engine = None
        _SessionLocal = None
        logger.info("🔒 Подключение к БД закрыто")


def get_session() -> Session:
    """
    Получение новой сессии для работы с БД

    Returns:
        Session: Сессия SQLAlchemy

    Raises:
        RuntimeError: Если БД не инициализирована
    """
    if _SessionLocal is None:
        raise RuntimeError("База данных не инициализирована. Вызовите init_db() сначала.")
    return _SessionLocal()


def get_db() -> Session:
    """
    Генератор для использования в FastAPI/Godot маршрутах.
    Обеспечивает автоматическое закрытие сессии после использования.

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = get_session()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Создание всех таблиц в базе данных (если их нет)"""
    if _engine is None:
        raise RuntimeError("База данных не инициализирована. Вызовите init_db() сначала.")

    # Проверяем, есть ли уже таблицы
    inspector = sa.inspect(_engine)
    existing_tables = inspector.get_table_names()

    # Создаем только если таблиц нет
    if not existing_tables:
        logger.info("Создание таблиц...")
        Base.metadata.create_all(bind=_engine)
        logger.info("✅ Таблицы успешно созданы")
    else:
        logger.info(f"ℹ️ Таблицы уже существуют: {existing_tables}")


def drop_tables() -> None:
    """Удаление всех таблиц (ОСТОРОЖНО! Удаляет все данные)"""
    if _engine is None:
        raise RuntimeError("База данных не инициализирована.")

    confirm = input("⚠️ Вы уверены, что хотите удалить ВСЕ таблицы? (yes/no): ")
    if confirm.lower() == 'yes':
        logger.warning("Удаление всех таблиц...")
        Base.metadata.drop_all(bind=_engine)
        logger.info("✅ Таблицы удалены")
    else:
        logger.info("❌ Удаление отменено")


# Функция-обертка для SessionLocal (исправление)
def SessionLocal() -> Session:
    """
    Возвращает новую сессию базы данных.
    Используется для обратной совместимости с существующим кодом.
    """
    return get_session()

def get_db_status() -> dict:
    """
    Получение статуса подключения к БД

    Returns:
        dict: Информация о состоянии БД
    """
    return {
        'initialized': _engine is not None,
        'engine': str(_engine) if _engine else None,
        'session_factory': _SessionLocal is not None,
        'tables': list(Base.metadata.tables.keys()) if _engine else []
    }
