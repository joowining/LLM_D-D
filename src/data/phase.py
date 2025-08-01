from enum import Enum

class GamePhase(Enum):
    introduction = "시작"
    exploration = "지역 탐험"
    interaction = "NPC 상호작용"
    management = "게임정보 확인"
    challenge = "던전 도전"
    search = "이벤트방 탐색"
    combat = "몬스터와 전투"
    general = "일반적인 질문"
    unknown = "알 수 없음"