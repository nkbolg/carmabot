import logging
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


class Handlers:
    def __init__(self, bot: aiogram.Bot, target_phrases):
        self.bot = bot
        self.target_phrases = target_phrases
        self.carma = {}

    async def start_handler(self, message: types.Message):
        reply_text = (
            "Привет! Я считаю карму в чатах.\n"
            "Я умею реагировать на следующие сообщения:\n\n"
            "{}".format("\n".join(self.target_phrases))
        )
        await message.reply(reply_text, reply=False)

    async def statistics_handler(self, message: types.Message):
        values = sorted(self.carma.values(), key=lambda x: x.carma, reverse=True)
        await message.reply("\n".join(map(str, values)))

    async def chat_reply_handler(self, message: types.Message):
        benefitiar_id = message.reply_to_message.from_user.id
        benefitiar_name = message.reply_to_message.from_user.full_name
        blesser_id = message.from_user.id
        blesser_name = message.from_user.full_name
        if benefitiar_id == blesser_id:
            await message.reply(
                "Полиция кармы подозревает вас в попытке накрутки😎\nНе надо так."
            )
            return
        if benefitiar_id not in self.carma:
            self.carma[benefitiar_id] = User(benefitiar_name)
        if blesser_id not in self.carma:
            self.carma[blesser_id] = User(blesser_name)
        self.carma[benefitiar_id] += 1
        reply_template = (
            f"{self.carma[blesser_id]} увеличил карму {self.carma[benefitiar_id]}"
        )
        if benefitiar_id == self.bot.id:
            reply_template += "\n\nХорошее слово и боту приятно❤"
        logging.info(message)
        await message.reply(reply_template)
