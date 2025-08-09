import json
import inspect

from states.GameSession import GameSessionState
from prompts.normal_prompt import NORMAL_VALIDATION_PROMPT
from llm.llm_setting import ChatModel

# 사용자의 입력을 받아서 저장하는 노드
def get_user_input_node(state: GameSessionState) -> GameSessionState:
    """사용자 입력을 받아 상태에 저장"""
    request = input("\n > ")

    return {
        "messages":[request]
    } 

# 사용자의 일반적인 입력에 대해서 이전 응답 메세지를 기반으로 개연성을 평가하는 노드
def validate_user_input_node(state: GameSessionState):
    """사용자의 입력과 LLM의 출력을 가져와서 그 개연성을 평가하고 참 거짓으로 판별하는 conditional node"""
    user_input = state["messages"][-1]
    system_output = state["system_messages"][-1]

    formatted_template = NORMAL_VALIDATION_PROMPT.invoke({
        "user_input": user_input,
        "system_output": system_output
    })

    result = json.loads(ChatModel.invoke(formatted_template))
    print(result["reason"], flush=True)
    if result["is_valid"]:
        return "exit"
    else:
        return "again"


# 현재까지의 게임 상태를 요약해서 정리하는 노드 

def summary_game_story_until_now(state:  GameSessionState):
    """현재까지의 사용자의 입력과 출력한 기본 내용과 선택을 바탕으로 게임흐름을 요약하는 노드"""
    pass

# 현재까지 추가된 메세지들을 갯수를 기반으로 요약 정리하는 노드 
def summary_user_input_from_latest_to_five(state: GameSessionState):
    """지금까지의 사용자의 상호작용 내용을 요약하는 노드 """
    pass