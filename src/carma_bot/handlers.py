import datetime
import logging
import shelve
from dataclasses import dataclass

import aiogram.utils.exceptions
from aiogram import types


@dataclass
class User:
    username: str
    carma: int = 0

    def __iadd__(self, other: int):
        self.carma += other
        return self

    def __str__(self):
        return f"{self.username} ({self.carma})"


class CarmaStorage:
    def __init__(self):
        self.filename = 'carma_storage'
        self.db = shelve.DbfilenameShelf(self.filename, writeback=True)
        if not self.db:
            self.db['all'] = {}
            self.db['last_month'] = {}
            self.db['current_month'] = datetime.datetime.utcnow().month
            self.db.sync()

    def inc(self, key: tuple[int, int]):
        self._flush_month(sync=False)

        self.db['all'][key] += 1
        self.db['last_month'][key] += 1
        self.db.sync()

    def conditional_emplace(self, key: tuple[int, int], name: str):
        self._flush_month(sync=False)

        if key not in self.db['all']:
            self.db['all'][key] = User(name)
            self.db['last_month'][key] = User(name)

        self.db.sync()

    def __getitem__(self, key: tuple[int, int]):
        return self.db['all'][key]

    def formatted_list_all(self, chat_id: int) -> str:
        filtered = (v for k, v in self.db['all'].items() if k[0] == chat_id)
        sorted_list = sorted(filtered, key=lambda x: x.carma, reverse=True)
        return "\n".join(map(str, sorted_list))

    def formatted_list_month(self, chat_id: int):
        filtered = (v for k, v in self.db['last_month'].items() if k[0] == chat_id)
        sorted_list = sorted(filtered, key=lambda x: x.carma, reverse=True)
        return "\n".join(map(str, sorted_list))

    def _flush_month(self, sync):
        now_month = datetime.datetime.utcnow().month

        if now_month != self.db['current_month']:
            assert now_month > self.db['current_month']
            self.db['last_month'] = {}
            self.db['current_month'] = now_month

        if sync:
            self.db.sync()


class Handlers:
    def __init__(self, bot: aiogram.Bot, target_phrases):
        self.bot = bot
        self.target_phrases = target_phrases
        self.carma = CarmaStorage()

    async def start_handler(self, message: types.Message):
        reply_text = (
            "Привет! Я считаю карму в чатах.\n"
            "Я умею реагировать на следующие сообщения:\n\n"
            "{}".format("\n".join(self.target_phrases))
        )
        await message.reply(reply_text, reply=False)

    async def statistics_handler(self, message: types.Message):
        if message.get_command().endswith('month'):
            await message.reply(self.carma.formatted_list_month(message.chat.id))
            return
        await message.reply(self.carma.formatted_list_all(message.chat.id))

    async def chat_reply_handler(self, message: types.Message):
        benefitiar_id = message.reply_to_message.from_user.id
        benefitiar_name = message.reply_to_message.from_user.full_name
        blesser_id = message.from_user.id
        blesser_name = message.from_user.full_name
        chat_id = message.chat.id
        benefitiar_key = chat_id, benefitiar_id
        blesser_key = chat_id, blesser_id
        if benefitiar_id == blesser_id:
            await message.reply(
                "Полиция кармы подозревает вас в попытке накрутки😎\nНе надо так."
            )
            return

        self.carma.conditional_emplace(key=benefitiar_key, name=benefitiar_name)
        self.carma.conditional_emplace(key=blesser_key, name=blesser_name)
        self.carma.inc((chat_id, benefitiar_id))
        reply_template = (
            f"{self.carma[blesser_key]} увеличил карму {self.carma[benefitiar_key]}"
        )
        if benefitiar_id == self.bot.id:
            reply_template += "\n\nХорошее слово и боту приятно❤"
        logging.info(message)
        await message.reply(reply_template)
