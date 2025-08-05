from typing import TypedDict, Annotated,List
from .Character import CharacterState
from enums.phase import GamePhase

from langgraph.graph.message import add_messages


class GameSessionState(TypedDict):
    # 사용자의 요청메세지 리스트
    messages: Annotated[List[str], add_messages]
    # 시스템의 생성메세지 리스트
    system_messages: Annotated[List[str], add_messages]
    # 게임 내에서 캐릭터의 상태에 대한 값
    character_state: CharacterState
    # 게임 내에서 어떤 상황에 있는가
    game_phase: GamePhase
    # 게임을 진행하면서 사용자가 처한 상태들을 요약한 내용 시스템메시지 5개당 생성, 최대 5개 유지
    game_context: Annotated[list[str], add_messages]
    # game_context전체와 이전까지의 story_summary를 요약한 내용
    story_summary: str
    # 하나의 노드에서 질문이 몇번 이루어졌는지 체크
    question_time: Annotated[int, lambda x: x>=0] = 0 
    cache_box: dict

