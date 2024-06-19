from aiogram.types import Message


def get_id(message: Message):
    return message.from_user.id  # type: ignore


def extract_arguments_from_message(message: Message) -> list[str]:
    args = message.text.split(" ")  # type: ignore
    args.remove(args[0])

    return args


def is_integer(string: str) -> bool:
    try:
        int(string)

        return True
    except ValueError:
        return False
