import json
from langgraph.graph import StateGraph, START, END
from llm.llm_setting import ChatModel, LLM
from states.GameSession import GameSessionState
from enums.phase import GamePhase

# graph 시각화용 패키지
from IPython.display import Image, display

from prompts.intro_prompt import intro_script, basic_game_script,create_intro_prompt, create_basic_game_rule_prompt 
from prompts.intro_prompt import race_prompt,race_choice_prompt, class_prompt, class_choice_prompt
from utils.intent_analysis import classify_intent
from tools.sqlite_tool import get_race_info, get_class_info, calculate_character_stats, list_available_options
from db.dnd_db import DnDDatabase
from util_node import get_user_input_node

db = DnDDatabase()

#####
def introduce_background_node(state: GameSessionState)-> GameSessionState:
    """현재 게임에 대한 배경을 설명"""
    # state 값 가져오기
    current_question_time = state["question_time"]

    # stage 1. 동적프롬프트 완성
    formatted_prompt = None 

    if current_question_time:
        intro_prompts = create_intro_prompt(True)
        formatted_prompt = intro_prompts.invoke({
            "origin": intro_script,
            "length": 20,
        })
    else:
        intro_prompts = create_intro_prompt(False)
        formatted_prompt = intro_prompts.invoke({
            "origin": intro_script,
            "usr_input": state["messages"][-1]
        })

    # stage 2. LLM으로부터 응답생성
    response = ChatModel.invoke(formatted_prompt) 
    summary = response.content

    ## 생성한 내용을 출력
    print(summary)
    # stage 4. 게임의 상태값 변경 
    return {
        "question_time": current_question_time + 1,
        "system_messages": [summary], # 리스트로 반환하여 add_messages활용
        "game_phase": GamePhase.introduction
    }

######
def explain_game_condition_node(state: GameSessionState)-> GameSessionState:
    """게임을 플레이하는 방법과 클리어 조건과 게임 오버 조건 설명"""
    # state값 가져오기
    current_question_time = state["question_time"]

    # stage 1. 동적프롬프트 완성
    formatted_prompt = None 

    if current_question_time:
        game_prompts = create_basic_game_rule_prompt(True)
        formatted_prompt = game_prompts.invoke({
            "origin": basic_game_script,
            "length": 20,
        })
    else:
        game_prompts = create_basic_game_rule_prompt(False)
        formatted_prompt = game_prompts.invoke({
            "origin": basic_game_script,
            "usr_input": state["messages"][-1]
        })

    # stage 2. LLM으로부터 응답생성
    response = ChatModel.invoke(formatted_prompt) 
    summary = response.content

    ## 생성한 내용을 출력
    print(summary)
    
    return {
        "question_time": current_question_time + 1,
        "system_messages": [summary],
        "game_phase": GamePhase.introduction
    }

def reset_question_time_node(state: GameSessionState)-> GameSessionState:
    """해당 노드에서 question이 종료될 때 리셋"""

    return {
        "question_time": 0
    }


####
def question_left_router(state: GameSessionState):
    """state로부터 값을 확인한 다음 조건 비교를 통해 다음 노드를 결정"""
    latest_message = state["messages"][-1] if state["messages"] else ""
    intent = classify_intent(latest_message)

    if intent == "POSITIVE":
        return "again"
    elif intent == "NEGATIVE":
        return  "exit"
    else:
        return "again"


def explain_race(state: GameSessionState)-> GameSessionState:
    """종족에 대한 데이터를 바탕으로 프롬프트 생성 """
    race_data = db.get_all_races()
    formatted_prompt = race_prompt.invoke({"race":race_data}) 
    response = ChatModel.invoke(formatted_prompt) 
    print(response.content)
    
    return {
        "system_messages": response.content
    }

####
def race_choice_analysis(state: GameSessionState)-> GameSessionState:
    """이전 노드에서 사용자의 입력값을 바탕으로 종족 선택 여부 판단 및 해당 종족이 DB에 존재하는지 여부 판단"""
    user_input = state["messages"][-1] if state["messages"] else ""
    race_data = db.get_all_race_names()

    formatted_prompt = race_choice_prompt.invoke({
        "race_data": race_data,
        "user_input": user_input
    })     

    response = ChatModel.invoke(formatted_prompt)
    response_dict = json.loads(response.content)
    intent, chosen_race, choice= response_dict["intent"], response_dict["race"], response_dict["choice"]

    return {
        "cache_box": {
            "intent": intent,
            "chosen_race": chosen_race,
            "choice": choice 
        }
    }

def race_choice_router(state: GameSessionState) -> str:
    """분석한 결과를 바탕으로 라우팅"""
    intent = state["cache_box"]["intent"]
    choice = state["cache_box"]["choice"]
    user_input = state["messages"][-1]

    if choice:
        return "exit"
    else:
        if intent == "information":
            race_data = db.get_all_races()
            formatted_prompt = race_prompt.invoke({"race":race_data, "user_input":user_input}) 
            response = ChatModel.invoke(formatted_prompt)  
            print(response.content)
        else:
            print("다음의 설명을 보고 적절한 종족을 선택하거나 물어봐주세요 ")
        return "again"

def race_fix(state: GameSessionState) -> GameSessionState:
    return {
        "charcter_state" : {
            "race": state["cache_box"]["chosen_race"]
        }
    }


def explain_class(state: GameSessionState) -> GameSessionState:
    """직업에 대한 데이터를 바탕으로 프롬프트 생성"""
    class_data = db.get_all_classes()
    formatted_prompt = class_prompt.invoke({"class":class_data})
    response = ChatModel.invoke(formatted_prompt)
    print(response.content)

    return {
        "system_messages": response.content
    }

def class_choice_analysis(state: GameSessionState) -> GameSessionState:
    """이전 노드에서 사용자의 입력값을 바탕으로 클래스 선택 여부 판단 및 해당 종족이 DB에 존재하는지 여부 판단"""
    user_input = state["messages"][-1] if state["messages"] else ""
    class_data = db.get_all_class_names()

    formatted_prompt = class_choice_prompt.invoke({
        "class_data": class_data,
        "user_input": user_input
    })     

    response = ChatModel.invoke(formatted_prompt)
    response_dict = json.loads(response.content)
    intent, chosen_class, choice= response_dict["intent"], response_dict["class"], response_dict["choice"]

    return {
        "cache_box": {
            "intent": intent,
            "chosen_class": chosen_class,
            "choice": choice 
        }
    }

def class_choice_router(state: GameSessionState)-> GameSessionState:
    """분석한 결과를 바탕으로 라우팅"""
    intent = state["cache_box"]["intent"]
    choice = state["cache_box"]["choice"]
    user_input = state["messages"][-1]

    if choice:
        return "exit"
    else:
        if intent == "information":
            class_data = db.get_all_classes()
            formatted_prompt = class_prompt.invoke({"class":class_data, "user_input":user_input}) 
            response = ChatModel.invoke(formatted_prompt)  
            print(response.content)
        else:
            print("다음의 설명을 보고 적절한 종족을 선택하거나 물어봐주세요 ")
        return "again"

def class_fix(state: GameSessionState)-> GameSessionState:
    return {
        "character_state":{
            "race": state["cache_box"]["chosen_class"]
        }
    }

def starting_location(state: GameSessionState)-> GameSessionState:
    """선택한 종족에 따라 시작하는 마을이 선택되었음을 알리고 그 마을을 상태값에 저장"""

    return state

"""
핵심 내용:

종족별 능력치 보너스 적용
직업별 초기 장비 지급:

무기 (검, 활, 지팡이 등)
방어구 (갑옷, 로브, 가죽 갑옷 등)
소모품 (물약, 화살, 마법 재료 등)
도구 (도적 도구, 치료 도구 등)


초기 소지금: 종족과 직업에 따른 차등 지급
특수 능력 활성화: 종족과 직업 조합에 따른 고유 스킬
능력치 총합 표시: 최종 스탯 정리 및 확인
"""
def initial_status_items(state: GameSessionState) -> GameSessionState:
    """ 선택한 종족과 직업에 따라 보너스 스테이터스와 초기장비를 지급하고 그 내용을 상태값에 저장"""

    return state


def dive_into_game(state: GameSessionState)-> GameSessionState:
    """ 현재까지 선택한 내용에 대해 알려주고 게임을 시작한다는 사인을 줌  """
    return state


tools = [get_race_info, get_class_info, calculate_character_stats, list_available_options]

graph = StateGraph(GameSessionState)
graph.add_node("introduction", introduce_background_node)
graph.add_node("reset_question_time",reset_question_time_node)
graph.add_node("user_input", get_user_input_node)
graph.add_node("question_router",question_left_router)
graph.add_node("explanation", explain_game_condition_node)
graph.add_node("explain_race", explain_race)
graph.add_node("race_choice_analysis", race_choice_analysis)
graph.add_node("race_router", race_choice_router)
graph.add_node("race_fix", race_fix)
graph.add_node("explain_class", explain_class)
graph.add_node("class_choice_analysis",class_choice_analysis)
graph.add_node("class_router",class_choice_router)
graph.add_node("class_fix",class_fix)
graph.add_node("starting_location", starting_location)
graph.add_node("initial_status_items", initial_status_items)
graph.add_node("dive_into_game", dive_into_game)

graph.add_edge(START, "introduction")
graph.add_edge("introduction", "user_input")
graph.add_conditional_edges(
    "user_input",
    question_left_router,
    {
        "again": "introduction",
        "exit": "reset_question_time"
    }
)
graph.add_edge("reset_question_time","explanation")
graph.add_edge("explanation","user_input")
graph.add_conditional_edges(
    "user_input",
    question_left_router,
    {
        "again": "explanation",
        "exit": "reset_question_time"
    }
)
graph.add_edge("reset_question_time", "explain_race")
graph.add_edge("explain_race","user_input")
graph.add_edge("user_input", "race_choice_analysis")
graph.add_conditional_edges(
    "race_choice_analysis",
    race_choice_router,
    {
        "again": "explain_race",
        "exit": "race_fix"
    }
)
graph.add_edge("race_fix","explain_class")
graph.add_edge("explain_class", "user_input")
graph.add_edge("user_input", "class_choice_analysis")
graph.add_conditional_edges(
    "class_choice_analysis",
    class_choice_router,
    {
        "again": "explian_class",
        "exit": "class_fix"
    }
)
graph.add_edge("class_fix", "starting_location")
graph.add_edge("starting_location","initial_status_items" )
graph.add_edge("initial_status_items", "dive_into_game")
graph.add_edge("dive_into_game", END)


result_graph = graph.compile()


def test_intro():
    pass

if __name__ == "__main__":
    # try:
    #     png_data = result_graph.get_graph().draw_mermaid_png()
    #     with open("intro_graph.png", "wb") as f:
    #         f.write(png_data)
    #     print("intro graph is saved as intro_graph.png")
    # except Exception as e:
    #     print(f" PNG save failed: {e}")
    #     print("ASCII TEXT visualization")
    #     print(result_graph.get_graph().draw_ascii())
    test_intro()