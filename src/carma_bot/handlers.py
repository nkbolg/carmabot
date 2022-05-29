import collections
import logging

import aiogram.utils.exceptions
from aiogram import types
from aiogram.types import ChatType


class Handlers:
    def __init__(self, bot: aiogram.Bot):
        self.bot = bot
        self.patterns = ['спасиб', 'спс', 'thanks']
        self.carma = collections.defaultdict(int)

    @staticmethod
    async def start_handler(message: types.Message):
        await message.reply("Привет! Я считаю карму в чатах.", reply=False)

    async def any_handler(self, message: types.Message):
        if message.chat.type != ChatType.GROUP:
            logging.info("Skipping non group message")
            return
        is_thankful_msg = message.text == '+'
        if is_thankful_msg is False:
            for pat in self.patterns:
                if pat in message.text:
                    is_thankful_msg = True
                    break
        if is_thankful_msg is False:
            logging.debug("Filtered out")
            return
        if message.reply_to_message is None:
            logging.debug("No reply, skipping")
            return
        benefitiar_id = message.reply_to_message.from_user.id
        benefitiar_name = message.reply_to_message.from_user.full_name
        blesser_id = message.from_user.id
        blesser_name = message.from_user.full_name
        if benefitiar_id == blesser_id:
            await message.reply("Полиция кармы подозревает вас в попытке накрутки😎\nНе надо так.")
            return
        self.carma[benefitiar_id] += 1
        self.carma[blesser_id] += 0
        reply_template = f"{blesser_name} ({self.carma[blesser_id]})" \
                         f" увеличил карму {benefitiar_name} ({self.carma[benefitiar_id]})"
        if benefitiar_id == self.bot.id:
            reply_template += "\nХорошее слово и боту приятно❤"
        logging.info(message)
        await message.reply(reply_template)
