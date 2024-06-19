import aiosqlite
from aiosqlite import IntegrityError
from entities import Admin, Specialization, Ticket


class NoSuchAdmin(Exception):
    pass


class AdminAlreadyExists(Exception):
    pass


class AdminRepo:
    def __init__(self, sqlite_path: str) -> None:

        self.__sqlite_path = sqlite_path

    async def update(self, admin: Admin):
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            conn.execute(
                "UPDATE admins SET window_number = ?, specialization = ? WHERE id = ?;",
                (admin.window_number, admin.specialization.value, admin.id),
            )
            await conn.commit()

    async def create(self, admin: Admin):
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            try:
                await conn.execute(
                    "INSERT INTO admins VALUES (?, ?, ?);",
                    (
                        admin.id,
                        admin.specialization.value,
                        admin.window_number,
                    ),
                )
                await conn.commit()
            except IntegrityError:
                raise AdminAlreadyExists()

    async def delete(self, admin: Admin):
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            conn.execute("DELETE FROM admins WHERE id = ?;", (admin.id,))
            await conn.commit()

    async def get_by_id(self, admin_id: int) -> Admin:
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            cursor = await conn.execute(
                "SELECT id, specialization, window_number "
                "FROM admins WHERE id = ?;",
                (admin_id,),
            )

            admin_data = await cursor.fetchone()

            if not admin_data:
                raise NoSuchAdmin()

            return Admin(
                id=admin_data[0],
                specialization=Specialization.get_from_string(admin_data[1]),
                window_number=admin_data[2],
            )

    async def init_table(
        self,
    ):
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            await conn.execute(
                "CREATE TABLE IF NOT EXISTS admins "
                "("
                "id INTEGER PRIMARY KEY, "
                "specialization TEXT NOT NULL, "
                "window_number INTEGER NOT NULL"
                ");"
            )
            await conn.commit()


class NoSuchTicket(Exception):
    pass


class TicketAlreadyExists(Exception):
    pass


class TicketRepo:
    def __init__(self, sqlite_path: str) -> None:

        self.__sqlite_path = sqlite_path

    async def create(self, ticket: Ticket):
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            try:
                await conn.execute(
                    "INSERT INTO tickets (user_id, specialization, date) "
                    "VALUES (?, ?, ?);",
                    (ticket.user_id, ticket.specialization.value, ticket.date),
                )
                await conn.commit()
            except IntegrityError:
                raise TicketAlreadyExists()

    async def update(self, ticket: Ticket):
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            await conn.execute(
                "UPDATE tickets SET specialization = ?, date = ? WHERE user_id = ?;",
                (ticket.specialization.value, ticket.date, ticket.user_id),
            )
            await conn.commit()

    async def delete(self, ticket: Ticket):
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            await conn.execute(
                "DELETE FROM tickets WHERE user_id = ?;", (ticket.user_id,)
            )
            await conn.commit()

    async def get_by_user_id(self, user_id: int) -> Ticket:
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            cursor = await conn.execute(
                "SELECT user_id, specialization, date FROM tickets WHERE user_id = ?;",
                (user_id,),
            )

            result = await cursor.fetchone()

            if not result:
                raise NoSuchTicket()

            return Ticket(
                result[0],
                Specialization.get_from_string(result[1]),
                result[2],
            )

    async def get_first_enqueued(self) -> Ticket:
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            cursor = await conn.execute(
                "SELECT user_id, specialization, date "
                "FROM tickets ORDER BY date LIMIT 1;"
            )

            result = await cursor.fetchone()

            if not result:
                raise NoSuchTicket()

            return Ticket(
                result[0],
                Specialization.get_from_string(result[1]),
                result[2],
            )

    async def init_table(
        self,
    ):
        async with aiosqlite.connect(self.__sqlite_path) as conn:
            await conn.execute(
                "CREATE TABLE IF NOT EXISTS tickets "
                "("
                "user_id INTEGER PRIMARY KEY, "
                "specialization TEXT NOT NULL, "
                "date timestamp NOT NULL"
                ");"
            )
            await conn.commit()
