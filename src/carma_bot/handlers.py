import datetime
import logging
import shelve
from typing import Union
from dataclasses import dataclass

import aiogram.utils.exceptions
from aiogram import types


@dataclass
class User:
    username: str = None
    name: str = None
    carma: int = 0

    def __iadd__(self, other: int):
        self.carma += other
        return self

    def __str__(self):
        return f"{self.name if self.name else self.username} ({self.carma})"

    def __hash__(self):
        return hash(self.username or "" + self.name or "")


class CarmaStorage:
    def __init__(self, filename):
        self.filename = filename
        self.db = shelve.DbfilenameShelf(self.filename, writeback=True)
        if not self.db:
            self.db["all"] = {}
            self.db["last_month"] = {}
            self.db["current_month"] = datetime.datetime.utcnow().month
            self.db.sync()

    def inc(self, key: Union[tuple[str, int], tuple[int, int]]):
        self._flush_month(sync=False)

        self.db["all"][key] += 1
        self.db["last_month"][key] += 1
        self.db.sync()

    @staticmethod
    def _inner_emplace(
        key: Union[tuple[str, int], tuple[int, int]], user: User, data_dict
    ):
        if key not in data_dict:
            data_dict[key] = user

    def conditional_emplace(
        self,
        *,
        chat_id: int,
        name: str = None,
        user_id: int = None,
        username: str = None,
    ):
        self._flush_month(sync=False)

        username_key = username, chat_id
        userid_key = user_id, chat_id

        # if mentioned by username earlier but not mentioned by user_id
        if username is not None and user_id is not None:
            if username_key in self.db["all"] and userid_key not in self.db["all"]:
                assert name is not None
                self.db["all"][username_key].name = name
                self.db["last_month"][username_key].name = name
                self.db["all"][userid_key] = self.db["all"][username_key]
                self.db["last_month"][userid_key] = self.db["last_month"][username_key]
                return

        user_all = User(username, name)
        user_month = User(username, name)
        key = None

        if user_id is not None:
            self._inner_emplace(userid_key, user_all, self.db["all"])
            self._inner_emplace(userid_key, user_month, self.db["last_month"])
            key = userid_key

        if username is not None:
            self._inner_emplace(username_key, user_all, self.db["all"])
            self._inner_emplace(username_key, user_month, self.db["last_month"])
            key = username_key

        assert key is not None

        self.db.sync()

        return key

    def __getitem__(self, key: Union[tuple[str, int], tuple[int, int]]):
        return self.db["all"][key]

    def formatted_list_all(self, chat_id: int) -> str:
        filtered = list(set(v for k, v in self.db["all"].items() if k[1] == chat_id and v.carma != 0))
        sorted_list = sorted(filtered, key=lambda x: x.carma, reverse=True)
        return "\n".join(map(str, sorted_list)) or "Пока тут пусто"

    def formatted_list_month(self, chat_id: int):
        filtered = list(set(v for k, v in self.db["last_month"].items() if k[1] == chat_id and v.carma != 0))
        sorted_list = sorted(filtered, key=lambda x: x.carma, reverse=True)
        return "\n".join(map(str, sorted_list)) or "Пока тут пусто"

    def _flush_month(self, sync):
        now_month = datetime.datetime.utcnow().month

        if now_month != self.db["current_month"]:
            assert now_month > self.db["current_month"]
            self.db["last_month"] = {}
            self.db["current_month"] = now_month

        if sync:
            self.db.sync()


class Handlers:
    def __init__(self, bot: aiogram.Bot, target_phrases):
        self.bot = bot
        self.target_phrases = target_phrases
        self.carma = CarmaStorage(filename="carma_storage")

    async def start_handler(self, message: types.Message):
        reply_text = (
            "Привет! Я считаю карму в чатах.\n"
            "Я умею реагировать на следующие слова:\n\n"
            "{}".format("\n".join(self.target_phrases))
        )
        await message.reply(reply_text, reply=False)

    async def statistics_handler(self, message: types.Message):
        if message.get_command().endswith("month"):
            await message.reply(self.carma.formatted_list_month(message.chat.id))
            return
        await message.reply(self.carma.formatted_list_all(message.chat.id))

    @staticmethod
    def _acceptable(target_phrases, text: str):
        lowered = text.lower()
        for phr in target_phrases:
            if phr in lowered:
                return True
        return False

    @staticmethod
    def parse_mentions(text: str) -> list[str]:
        if "@" not in text:
            return []
        return [x[1:].rstrip() for xs in text.split() for x in xs.split(',') if x.startswith("@")]

    async def chat_reply_handler(self, message: types.Message):
        if not self._acceptable(self.target_phrases, message.text):
            logging.debug("Message not acceptable")
            return

        benefitiar_id = message.reply_to_message.from_user.id
        benefitiar_name = message.reply_to_message.from_user.full_name
        benefitiar_username = message.reply_to_message.from_user.username
        blesser_id = message.from_user.id
        blesser_name = message.from_user.full_name
        blesser_username = message.from_user.username
        chat_id = message.chat.id
        if benefitiar_id == blesser_id:
            await message.reply(
                "Полиция кармы подозревает вас в попытке накрутки😎\n\nНе надо так."
            )
            return

        benefitiar_user_key = self.carma.conditional_emplace(
            chat_id=chat_id,
            username=benefitiar_username,
            user_id=benefitiar_id,
            name=benefitiar_name,
        )
        blesser_user_key = self.carma.conditional_emplace(
            chat_id=chat_id,
            username=blesser_username,
            user_id=blesser_id,
            name=blesser_name,
        )
        self.carma.inc((benefitiar_id, chat_id))
        reply_template = f"{self.carma[blesser_user_key]} увеличил карму {self.carma[benefitiar_user_key]}"
        if benefitiar_id == self.bot.id:
            reply_template += "\n\nХорошее слово и боту приятно❤"
        logging.info(message)
        await message.reply(reply_template)

    async def chat_mentions_handler(self, message: types.Message):
        if not (mentioned_users := self.parse_mentions(message.text)):
            logging.debug("No mentions")
            return

        if not self._acceptable(self.target_phrases, message.text):
            logging.debug("Message not acceptable")
            return

        blesser_id = message.from_user.id
        blesser_name = message.from_user.full_name
        chat_id = message.chat.id
        blesser_username = message.from_user.username

        blesser_user_key = self.carma.conditional_emplace(
            chat_id=chat_id,
            username=blesser_username,
            user_id=blesser_id,
            name=blesser_name,
        )

        benefitiar_users = [self.carma.conditional_emplace(
            chat_id=chat_id,
            username=username
        ) for username in mentioned_users if username != blesser_username]

        if not benefitiar_users:
            await message.reply(
                "Полиция кармы подозревает вас в попытке накрутки😎\nНе надо так."
            )
            return

        reply_template = f"{self.carma[blesser_user_key]} увеличил карму:\n\n"

        for key in benefitiar_users:
            self.carma.inc(key)
            reply_template += f"{self.carma[key]}\n"

        logging.info(message)
        await message.reply(reply_template)

