from typing import TypedDict
from enums.race import RaceEnum
from enums.profession import ProfessionEnum
from .Status import Status

class CharacterState(TypedDict):
    name: str
    race: RaceEnum
    profession: ProfessionEnum
    status: Status
    location_type: str
    location: str
