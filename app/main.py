import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from controllers import AdminController
from enrollee_queue import EnrolleeQueue
from entities import Admin, Specialization
from repos import AdminRepo, TicketRepo
from settings import app_settings
from utils import extract_arguments_from_message, get_id, is_integer

# All handlers should be attached to the Router (or Dispatcher)


admin_controller = AdminController(
    admin_repo=AdminRepo(app_settings.SQLITE_PATH)
)

enrollee_queue = EnrolleeQueue(
    ticket_repo=TicketRepo(app_settings.SQLITE_PATH)
)

bot = Bot(
    token=app_settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()


class TextMessages:

    CONSULTATION_CHOICE_BUTTON_TEXT = "Консультация"

    DOCUMENTS_CHOICE_BUTTON_TEXT = "Подача документов"

    START_MESSAGE = "Привет, выбери необходимое действие!"

    NOT_ENOUGH_RIGHTS_MESSAGE = "Извини, но тебе этого делать нельзя :("

    EMPTY_ENROLLEE_QUEUE_MESSAGE = "Никого нет в очереди"

    ADMIN_ENROLLEE_DEQUEUE_MESSAGE = (
        "Абитуриент из очереди направлен к Вашему окну"
    )

    ADMIN_TRIED_USELESS_ACTION_MESSAGE = (
        "Ты же админ, зачем тебе это делать? XD"
    )

    TICKET_IS_ALREADY_IN_QUEUE_MESSAGE = (
        "Такой талон уже выдан, подождите, пожалуйста. :)"
    )

    TICKET_SUCCESSFULLY_CREATED_MESSAGE = (
        "Талон успешно выдан! Вам осталось только чуть-чуть подождать. :)"
    )

    INCORRECT_ARGUMENTS_WHEN_ADMIN_ADDING_MESSAGE = (
        "Неверные аргументы.\n"
        "Первый должен быть ID пользователя "
        "(получается через команду /id от самого пользователя)\n"
        "Второй должен быть элементов следующего списка: DOCUMENTS, CONSULTATION,\n"
        "Третий должен быть целым числом, обозначающим номер окна."
    )

    @staticmethod
    def get_enrollee_dequeue_message(window_number: int):
        return (
            f"Ваше окно под номером <b>{window_number}</b>. "
            f"Пройдите к нему, пожалуйста. :)"
        )


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    start_user_keyboard_builder = ReplyKeyboardBuilder()

    start_user_keyboard_builder.button(
        text=TextMessages.DOCUMENTS_CHOICE_BUTTON_TEXT
    ).button(text=TextMessages.CONSULTATION_CHOICE_BUTTON_TEXT)

    await message.answer(
        TextMessages.START_MESSAGE,
        reply_markup=start_user_keyboard_builder.as_markup(),
    )


async def create_ticket_with_specialization(
    message: Message, specialization: Specialization
):
    admin = await admin_controller.get_admin(get_id(message))

    if admin:
        await message.answer(TextMessages.ADMIN_TRIED_USELESS_ACTION_MESSAGE)
        return

    try:
        await enrollee_queue.enqueue(
            user_id=get_id(message), specialization=specialization
        )
        await message.answer(TextMessages.TICKET_SUCCESSFULLY_CREATED_MESSAGE)
    except EnrolleeQueue.SameTicketEnqueueError:
        await message.answer(TextMessages.TICKET_IS_ALREADY_IN_QUEUE_MESSAGE)


@dp.message(
    lambda message: message.text == TextMessages.DOCUMENTS_CHOICE_BUTTON_TEXT
)
async def message_documents_handler(message: Message) -> None:
    logging.debug("here")
    await create_ticket_with_specialization(message, Specialization.DOCUMENTS)


@dp.message(
    lambda message: message.text
    == TextMessages.CONSULTATION_CHOICE_BUTTON_TEXT
)
async def message_consultation_handler(message: Message) -> None:
    await create_ticket_with_specialization(
        message, Specialization.CONSULTATION
    )


@dp.message(Command(commands=["id"]))  # type: ignore
async def message_id_handler(message: Message) -> None:
    await message.answer(f"Ваш ID: {get_id(message)}")


async def require_admin(message: Message) -> Admin | None:

    admin = await admin_controller.get_admin(get_id(message))

    if not admin:
        await message.answer(TextMessages.NOT_ENOUGH_RIGHTS_MESSAGE)
        return

    return admin


@dp.message(Command(commands=["next"]))  # type: ignore
async def command_next_handler(message: Message) -> None:
    admin = await require_admin(message)

    if not admin:
        return

    try:
        ticket = await enrollee_queue.dequeue(
            admin_id=get_id(message)  # type: ignore
        )
    except EnrolleeQueue.NoTicketsInQueue:
        await message.answer(TextMessages.EMPTY_ENROLLEE_QUEUE_MESSAGE)
        return

    await message.answer("Абитуриент из очереди направлен к Вашему окну")

    await bot.send_message(
        ticket.user_id,
        TextMessages.get_enrollee_dequeue_message(admin.window_number),
    )


def is_specialization_valid(argument: str) -> bool:
    try:
        Specialization.get_from_string(argument)

    except ValueError:
        return False

    return True


def is_user_id_valid(argument: str) -> bool:
    return is_integer(argument)


def is_window_number_valid(argument: str) -> bool:
    return is_integer(argument)


@dp.message(lambda message: message.text.startswith("/addadmin"))
async def command_addadmin_handler(message: Message):
    if not await admin_controller.is_owner(get_id(message)):
        await message.answer("Эта команда разрешена только владельцу бота")

        return

    args = extract_arguments_from_message(message)

    if (
        len(args) != 3
        or not is_user_id_valid(args[0])
        or not is_specialization_valid(args[1])
        or not is_window_number_valid(args[2])
    ):
        await message.answer(
            TextMessages.INCORRECT_ARGUMENTS_WHEN_ADMIN_ADDING_MESSAGE
        )

    user_id = int(args[0])
    specialization = Specialization.get_from_string(args[1])
    window_number = int(args[2])

    try:
        await admin_controller.add_admin(
            user_id, specialization, window_number
        )
    except AdminController.AdminAlreadyExists:
        await message.answer("Админ с таким ID уже существует")


async def main() -> None:

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
