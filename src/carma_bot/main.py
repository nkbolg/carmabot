import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from carma_bot.carma_storage import CarmaStorage
from carma_bot.config import Settings
from carma_bot.handlers import router as main_router
from carma_bot.middleware import UpdatesDumperMiddleware

from carma_bot.phrases import phrases_list


async def async_main():
    """Точка входа в приложение"""

    # включение логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s: "
               "%(filename)s: "
               "%(levelname)s: "
               "%(funcName)s(): "
               "%(lineno)d:\t"
               "%(message)s",
    )

    logging.info("Application started")

    settings = Settings()

    bot = Bot(settings.bot_token.get_secret_value())
    storage = MemoryStorage()
    carma_storage = CarmaStorage(filename="carma_storage")
    dispatcher = Dispatcher(storage=storage, settings=settings, phrases=phrases_list, carma_storage=carma_storage)
    dispatcher.include_router(main_router)
    dispatcher.update.outer_middleware(UpdatesDumperMiddleware())

    await dispatcher.start_polling(bot)

    logging.info("Application shut down")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
