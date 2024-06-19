from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Specialization(Enum):
    DOCUMENTS = "DOCUMENTS"
    CONSULTATION = "CONSULTATION"

    @staticmethod
    def get_from_string(string: str) -> Specialization:
        match string:
            case "DOCUMENTS":
                return Specialization.DOCUMENTS
            case "CONSULTATION":
                return Specialization.CONSULTATION
            case _:
                raise ValueError(
                    "Incorrect specialization, this should have never happened"
                )


@dataclass
class Admin:
    id: int
    specialization: Specialization
    window_number: int


@dataclass
class Ticket:
    user_id: int
    specialization: Specialization
    date: datetime
