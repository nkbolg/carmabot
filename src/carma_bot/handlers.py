import datetime
import logging

from aiogram import types, Router, exceptions, F, Bot
from aiogram.filters import CommandStart, Command

from carma_bot.carma_storage import CarmaStorage
from carma_bot.config import Settings

router = Router(name="main_router")


@router.message(CommandStart())
async def start_handler(message: types.Message, phrases: list[str]):
    reply_text = (
        "Привет! Я считаю карму в чатах.\n"
        "Я умею реагировать на следующие слова:\n\n"
        "{}".format("\n".join(phrases))
    )
    await message.reply(reply_text, reply=False)


@router.message(Command("statsmonth"))
async def month_statistics_handler(message: types.Message, carma_storage: CarmaStorage):
    await message.reply(carma_storage.formatted_list_month(message.chat.id))


@router.message(Command("stats"))
async def all_statistics_handler(message: types.Message, carma_storage: CarmaStorage):
    await message.reply(carma_storage.formatted_list_all(message.chat.id))


def _acceptable(phrases, text: str):
    lowered = text.lower()
    return any(phr in lowered for phr in phrases)


def parse_mentions(text: str) -> list[str]:
    if "@" not in text:
        return []
    return [x[1:].rstrip() for xs in text.split() for x in xs.split(',') if x.startswith("@")]


@router.message(F.reply_to_message, F.text, F.chat.type.in_({"group", "supergroup"}))
async def chat_reply_handler(message: types.Message, phrases: list[str], carma_storage: CarmaStorage,
                             bot: Bot):
    if not _acceptable(phrases, message.text):
        logging.debug("Message not acceptable")
        return

    benefitiar_id = message.reply_to_message.from_user.id
    benefitiar_name = message.reply_to_message.from_user.full_name
    benefitiar_username = message.reply_to_message.from_user.username
    blesser_id = message.from_user.id
    blesser_name = message.from_user.full_name
    blesser_username = message.from_user.username
    chat_id = message.chat.id

    now_month = datetime.datetime.utcnow().month
    if now_month != carma_storage.db["current_month"]:
        kir_chats = [-100600741090]
        for kir_chat in kir_chats:
            month_msg = carma_storage.formatted_list_month(kir_chat)
            logging.info(month_msg)
            if len(month_msg) > 4000:
                month_msg = month_msg[:4000] + '...'
            await bot.send_message(kir_chat, f"Статистика за месяц:\n\n{month_msg}")

    if benefitiar_id == blesser_id:
        await message.reply(
            "Полиция кармы подозревает вас в попытке накрутки😎\n\nНе надо так."
        )
        return

    benefitiar_user_key = carma_storage.conditional_emplace(
        chat_id=chat_id,
        username=benefitiar_username,
        user_id=benefitiar_id,
        name=benefitiar_name,
    )
    blesser_user_key = carma_storage.conditional_emplace(
        chat_id=chat_id,
        username=blesser_username,
        user_id=blesser_id,
        name=blesser_name,
    )
    carma_storage.inc((benefitiar_id, chat_id))
    reply_template = f"{carma_storage[blesser_user_key]} увеличил карму {carma_storage[benefitiar_user_key]}"
    if benefitiar_id == bot.id:
        reply_template += "\n\nХорошее слово и боту приятно❤"
    logging.info(message)
    try:
        await message.reply(reply_template)
    except exceptions.TelegramBadRequest:
        logging.exception("Exception while trying to reply to msg")


@router.message(F.text, F.chat.type.in_({"group", "supergroup"}))
async def chat_mentions_handler(message: types.Message, settings: Settings, phrases: list[str],
                                carma_storage: CarmaStorage,
                                bot: Bot):
    if not (mentioned_users := parse_mentions(message.text)):
        logging.debug("No mentions")
        return

    if not _acceptable(phrases, message.text):
        logging.debug("Message not acceptable")
        return

    blesser_id = message.from_user.id
    blesser_name = message.from_user.full_name
    chat_id = message.chat.id
    blesser_username = message.from_user.username

    now_month = datetime.datetime.utcnow().month
    if now_month != carma_storage.db["current_month"]:
        for kir_chat in settings.target_chats:
            month_msg = carma_storage.formatted_list_month(kir_chat)
            logging.info(month_msg)
            if len(month_msg) > 4000:
                month_msg = month_msg[:4000] + '...'
            await bot.send_message(kir_chat, f"Статистика за месяц:\n\n{month_msg}")

    blesser_user_key = carma_storage.conditional_emplace(
        chat_id=chat_id,
        username=blesser_username,
        user_id=blesser_id,
        name=blesser_name,
    )

    benefitiar_users = [carma_storage.conditional_emplace(
        chat_id=chat_id,
        username=username
    ) for username in mentioned_users if username != blesser_username]

    if not benefitiar_users:
        await message.reply(
            "Полиция кармы подозревает вас в попытке накрутки😎\nНе надо так."
        )
        return

    reply_template = f"{carma_storage[blesser_user_key]} увеличил карму:\n\n"

    for key in benefitiar_users:
        carma_storage.inc(key)
        reply_template += f"{carma_storage[key]}\n"

    logging.info(message)
    await message.reply(reply_template)
