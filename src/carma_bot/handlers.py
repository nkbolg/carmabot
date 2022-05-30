import collections
import logging

import aiogram.utils.exceptions
from aiogram import types


class Handlers:
    def __init__(self, bot: aiogram.Bot, target_phrases):
        self.bot = bot
        self.target_phrases = target_phrases
        self.carma = collections.defaultdict(int)

    async def start_handler(self, message: types.Message):
        reply_text = "Привет! Я считаю карму в чатах.\n" \
                     "Я умею реагировать на следующие сообщения:\n\n" \
                     "{}".format('\n'.join(self.target_phrases))
        await message.reply(reply_text, reply=False)

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
        self.carma[benefitiar_id] += 1
        self.carma[blesser_id] += 0
        reply_template = (
            f"{blesser_name} ({self.carma[blesser_id]})"
            f" увеличил карму {benefitiar_name} ({self.carma[benefitiar_id]})"
        )
        if benefitiar_id == self.bot.id:
            reply_template += "\nХорошее слово и боту приятно❤"
        logging.info(message)
        await message.reply(reply_template)
