from typing import TypedDict
from data.race import RaceEnum
from data.profession import ProfessionEnum

class CharacterState(TypedDict):
    name: str
    race: RaceEnum
    profession: ProfessionEnum