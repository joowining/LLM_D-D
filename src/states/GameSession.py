from typing import TypedDict, Annotated,List
from .Character import CharacterState
from data.phase import GamePhase

from langgraph.graph.message import add_messages


class GameSessionState(TypedDict):
    messages: Annotated[List[str], add_messages]
    character_state: CharacterState
    game_phase: GamePhase


