from typing import TypedDict
from enum import Enum


# langchain
from langchain_core.prompts import PromptTemplate

# langgraph
from langgraph.graph import StateGraph, START, END

class RaceEnum(str,Enum):
    HUMAN = "인간"
    ELF = "엘프"
    WAREWOLF = "늑대인간"
    BARBARIAN = "야만인"
    DWARF = "드워프"

class ClassEnum(str, Enum):
    WARRIOR = "전사"
    MONK = "무도가"
    PALADIN = "성기사"
    HUNTER = "사냥꾼"
    ROGUE = "도적"
    BARD = "바드"
    PRIEST = "사제"
    WALOCK = "흑마법사"
    WIZARD = "마법사"
    

class CharacterState(TypedDict):
    name: str
    race: RaceEnum
    profession: ClassEnum

class GameState(TypedDict):
    ch_state: CharacterState


def choose_race(state: GameState) -> GameState:
    pass 

def check_chosen_race(state: GameState)-> GameState:
    races = [race.name for race in RaceEnum]
    if state["ch_state"]["race"] in races:
        return "continues"
    else :
        return "choose_race"

def continues(state: GameState) -> GameState:
    return state


