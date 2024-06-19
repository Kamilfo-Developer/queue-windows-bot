import os

from dotenv import load_dotenv


class AppSettings:
    BOT_TOKEN: str
    OWNER_ID: int
    SQLITE_PATH: str

    def __init__(self) -> None:
        load_dotenv()
        BOT_TOKEN = os.getenv("BOT_TOKEN")

        if not BOT_TOKEN:
            raise EnvironmentError("BOT_TOKEN is not defined in .env file")

        self.BOT_TOKEN = BOT_TOKEN

        OWNER_ID = os.getenv("OWNER_ID")

        if not OWNER_ID:
            raise EnvironmentError("OWNER_ID is not defined in .env file")

        try:
            self.OWNER_ID = int(OWNER_ID)
        except ValueError:
            raise EnvironmentError(
                "OWNER_ID in .env file should be a telegram chat user id (integer)"
            )

        SQLITE_PATH = os.getenv("SQLITE_PATH")

        if not SQLITE_PATH:
            raise EnvironmentError("SQLITE_PATH is not defined in .env file")

        self.SQLITE_PATH = SQLITE_PATH


app_settings = AppSettings()
