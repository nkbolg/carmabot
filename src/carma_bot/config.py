from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: SecretStr
    target_chats: list[int]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
