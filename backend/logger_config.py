import logging

def get_logger(name: str):
    """
    Возвращает логгер с именем.
    Используется вместо прямого logging.getLogger()
    """
    return logging.getLogger(name)
