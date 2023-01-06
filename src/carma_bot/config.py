import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str


def get_config():
    """Получение конфигурации из переменных среды или .env файла."""
    # загрузка переменных среды из .env-файла при его наличии
    load_dotenv()

    # чтение данных из переменных среды
    token = os.environ["BOT_TOKEN"]

    return Config(token)
