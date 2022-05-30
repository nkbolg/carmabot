import asyncio

import aiogram
from aiogram import types
from aiogram.dispatcher import filters

from carma_bot import config
from carma_bot.handlers import Handlers


def create_dispatcher(conf: config.Config):
    """Создание и настройка поведения бота"""
    loop = asyncio.get_event_loop()
    bot = aiogram.Bot(conf.bot_token, loop)
    dispatcher = aiogram.Dispatcher(bot, loop)

    setup_handlers(dispatcher, conf)

    return dispatcher


def setup_handlers(dispatcher: aiogram.Dispatcher, conf: config.Config):
    """Привязка обработчиков к командам получаемым ботом"""
    target = ["спс", "спасибо", "благодарю", "thank you", "thanks"]

    handlers = Handlers(dispatcher.bot, target)

    dispatcher.register_message_handler(handlers.start_handler, filters.CommandStart())

    dispatcher.register_message_handler(
        handlers.chat_reply_handler,
        filters.Text(equals=target, ignore_case=True),
        is_reply=True,
        chat_type=types.ChatType.GROUP,
    )
