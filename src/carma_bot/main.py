import logging

from aiogram.utils import executor

from carma_bot.bot_setup import create_dispatcher
from carma_bot.config import get_config


def main():
    """Точка входа в приложение."""
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

    # получение класса хранящего конфигурируемые параметры
    conf = get_config()

    # создание и запуск объекта бота
    dispatcher = create_dispatcher(conf)

    executor.start_polling(dispatcher, skip_updates=True, loop=dispatcher.loop)

    logging.info("Application shut down")


if __name__ == "__main__":
    main()
