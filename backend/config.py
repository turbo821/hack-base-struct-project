import os

class Config:
    # === НАСТРОЙКИ БАЗЫ ДАННЫХ ===
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE = f'sqlite:///{os.path.join(BASE_DIR, "server.db")}'
