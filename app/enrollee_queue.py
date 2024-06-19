from datetime import datetime

from entities import Specialization, Ticket
from repos import NoSuchTicket, TicketRepo


class EnrolleeQueue:
    class SameTicketEnqueueError(Exception):
        pass

    class NoTicketsInQueue(Exception):
        pass

    def __init__(self, ticket_repo: TicketRepo) -> None:
        self.__ticket_repo = ticket_repo

    async def enqueue(
        self, user_id: int, specialization: Specialization
    ) -> None:
        try:
            ticket = await self.__ticket_repo.get_by_user_id(user_id)

            if ticket.specialization == specialization:
                raise self.SameTicketEnqueueError()

            ticket.specialization = specialization

            await self.__ticket_repo.update(ticket)

        except NoSuchTicket:
            await self.__ticket_repo.create(
                Ticket(user_id, specialization, datetime.now())
            )

    async def dequeue(self, admin_id: int) -> Ticket:
        try:
            ticket = await self.__ticket_repo.get_first_enqueued()

            await self.__ticket_repo.delete(ticket)

            return ticket

        except NoSuchTicket:
            raise self.NoTicketsInQueue()
