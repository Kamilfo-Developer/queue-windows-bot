from entities import Admin, Specialization
from repos import AdminAlreadyExists, AdminRepo, NoSuchAdmin
from settings import app_settings


class AdminController:

    class AdminAlreadyExists(Exception):
        pass

    def __init__(self, admin_repo: AdminRepo) -> None:
        self.__admin_repo = admin_repo

    async def is_admin(self, user_id: int) -> bool:
        try:
            await self.__admin_repo.get_by_id(user_id)
            return True
        except NoSuchAdmin:
            return False

    async def get_admin(self, user_id: int) -> Admin | None:
        try:
            return await self.__admin_repo.get_by_id(user_id)
        except NoSuchAdmin:
            return None

    async def is_owner(self, user_id: int) -> bool:
        return user_id == app_settings.OWNER_ID

    async def add_admin(
        self, user_id: int, specialization: Specialization, window_number: int
    ):
        try:
            await self.__admin_repo.create(
                Admin(user_id, specialization, window_number)
            )
        except AdminAlreadyExists:
            raise AdminAlreadyExists()
