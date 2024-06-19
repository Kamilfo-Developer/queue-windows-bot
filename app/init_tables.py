import asyncio

from repos import AdminRepo, TicketRepo
from settings import app_settings


async def init_tables() -> None:
    admin_repo = AdminRepo(app_settings.SQLITE_PATH)
    ticket_repo = TicketRepo(app_settings.SQLITE_PATH)

    await asyncio.gather(admin_repo.init_table(), ticket_repo.init_table())

    print("Tables created")


asyncio.run(init_tables())
