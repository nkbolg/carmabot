import asyncio

import aiogram

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
    handlers = Handlers(dispatcher.bot)

    dispatcher.register_message_handler(handlers.start_handler, commands=["start"])

    dispatcher.register_message_handler(handlers.any_handler)

    # dispatcher.register_message_handler(
    #     handlers.details_handler, regexp=f"^{MainButtons.DETAILS_SERVICE_BTN_TEXT}$"
    # )
    #
    # main_regex = f"^({'|'.join(MainButtons.get_texts()[1:])})$"
    # dispatcher.register_message_handler(handlers.create_chat_handler, regexp=main_regex)
    #
    # details_regex = f"^{'|'.join(DetailsMenuButtons.get_texts())}$"
    # dispatcher.register_message_handler(
    #     handlers.show_details_handler, regexp=details_regex
    # )
