from states.GameSession import GameSessionState

# 사용자의 입력을 받아서 저장하는 노드
def get_user_input_node(state: GameSessionState):
    """사용자 입력을 받아 상태에 저장"""
    request = input("\n >> ")

    return {
        "messages":[request]
    } 

# 현재까지의 게임 상태를 요약해서 정리하는 노드 



# 현재까지 추가된 메세지들을 갯수를 기반으로 요약 정리하는 노드 