import json
import inspect
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from llm.llm_setting import ChatModel
from states.GameSession import GameSessionState
from enums.phase import GamePhase

# graph 시각화용 패키지
from IPython.display import Image, display

from prompts.intro_prompt import intro_script, basic_game_script,create_intro_prompt, create_basic_game_rule_prompt 
from prompts.intro_prompt import race_prompt,race_choice_prompt, class_prompt, class_choice_prompt
from prompts.intro_prompt import CHARACTER_NAME_REQUEST_PROMPT, CHARACTER_NAME_VALIDATION_PROMPT
from prompts.intro_prompt import GAME_START_PROMPT
from utils.intent_analysis import classify_intent
from tools.sqlite_tool import get_race_info, get_class_info, calculate_character_stats, list_available_options
from db.dnd_db import DnDDatabase
from .util_nodes import get_user_input_node, validate_user_input_node

db = DnDDatabase("/home/joowon/my_develop/LLM_DND/src/db/DnD.db")

#####
def introduce_background_node(state: GameSessionState)-> GameSessionState:
    """현재 게임에 대한 배경을 설명"""
    # state 값 가져오기
    current_question_time = state["question_time"]

    # stage 1. 동적프롬프트 완성
    formatted_prompt = None 

    if current_question_time==0:
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
    print("🤖 LLM 응답 생성 중...", flush=True)  # 중간 과정 출력
    response = ChatModel.invoke(formatted_prompt) 
    summary = response.content

    ## 생성한 내용을 출력
    print(summary)

    # stage 4. 게임의 상태값 변경 
    return {
        "question_time": current_question_time + 1,
        "system_messages": [summary], # 리스트로 반환하여 add_messages활용
        "game_phase": GamePhase.introduction,
        "game_context": [summary]
    }

######
def explain_game_condition_node(state: GameSessionState)-> GameSessionState:
    """게임을 플레이하는 방법과 클리어 조건과 게임 오버 조건 설명"""
    # state값 가져오기
    current_question_time = state["question_time"]

    # stage 1. 동적프롬프트 완성
    formatted_prompt = None 

    if current_question_time==0:
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
    print(summary, flush=True)
    
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
        return "exit"
    elif intent == "NEGATIVE":
        return  "again"
    else:
        return "again"


def explain_race(state: GameSessionState)-> GameSessionState:
    """종족에 대한 데이터를 바탕으로 프롬프트 생성 """
    race_data = db.get_all_races()
    context = state["game_context"]
    formatted_prompt = race_prompt.invoke({"race":race_data, "context":context}) 
    response = ChatModel.invoke(formatted_prompt) 
    # 생성한 내용을 출력
    print(response.content, flush=True)
    
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
        "user_input": user_input.content
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
            # 생성한 내용을 출력
            print(response.content, flush=True)
        else:
            # 일반 내용 출력
            print("다음의 설명을 보고 선택지 내의 적절한 종족을 선택하거나 물어봐주세요 ( 한글로 )",flush=True)
        return "again"

def race_fix(state: GameSessionState) -> GameSessionState:
    old_character_state = state["character_state"]
    updated_character_state = {
        **old_character_state,
        "race": state["cache_box"]["chosen_race"]
    }
    return {
        "character_state" : updated_character_state
    }


def explain_class(state: GameSessionState) -> GameSessionState:
    """직업에 대한 데이터를 바탕으로 프롬프트 생성"""
    class_data = db.get_all_classes()
    context = state["game_context"]
    formatted_prompt = class_prompt.invoke({"class":class_data, "context":context})
    response = ChatModel.invoke(formatted_prompt)
    # 생성한 내용을 출력
    print(response.content,flush=True)

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
    # print detail
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
            print(response.content, flush=True)
        else:
            print("다음의 설명을 보고 적절한 종족을 선택하거나 물어봐주세요 ", flush=True)
        return "again"

def class_fix(state: GameSessionState)-> GameSessionState:
    old_character_state = state["character_state"]
    updated_character_state = {
        **old_character_state,
        "profession": state["cache_box"]["chosen_class"]
    }
    return {
        "character_state":updated_character_state
    }


##### 사용자에게 캐릭터 이름 입력 요구 
def enter_character_name(state: GameSessionState)-> GameSessionState:
    """"""
    # llm output
    context = state["game_context"]
    message = CHARACTER_NAME_REQUEST_PROMPT.invoke({"context":context})
    guidance_message = ChatModel.invoke(message)
    print(guidance_message.content, flush=True)

    return {
        "system_messages": [guidance_message]
    }

### input_node로 메세지를 받음

### validation을 거쳐서 적절한 아이디인지 아닌지를 결정하는 conditional node
def validate_character_name_router(state: GameSessionState) -> str:
    user_input = state["messages"]

    formatted_template = CHARACTER_NAME_VALIDATION_PROMPT.invoke({ "user_input":user_input})
    result = json.loads(ChatModel.invoke(formatted_template).content)

    if result["status"] == "VALID":
        return "exit"
    else:
        print(result["reason"], flush=True)
        return "again"


def extract_character_name_node(state: GameSessionState) -> GameSessionState:
    """별도 노드로 캐릭터 이름만 추출"""
    
    CHARACTER_EXTRACTION_PROMPT = ChatPromptTemplate.from_template(
        """
        다음 사용자 입력에서 캐릭터 이름이 언급되었는지 확인하고 추출해주세요.
        
        사용자 입력: {user_input}
        
        JSON 형식으로만 응답해주세요:
        {{
            "character_name": "캐릭터 이름" (없으면 null)
        }}
        """
    )
    
    chain = CHARACTER_EXTRACTION_PROMPT | ChatModel
    
    response = chain.invoke({"user_input": state["messages"][-1]})
    
    try:
        result = json.loads(response.content)
        character_name = result.get("character_name")
        
        if character_name:
            old_character_state = state["character_state"]
            updated_character_state = {
                **old_character_state,
                "name": character_name
            }

            return {
                "character_state":updated_character_state
            }
        else:
            return {}
            
    except json.JSONDecodeError:
        return {}


### validation성공 -> 저장하고 다음 노드로 
### validation실패 -> 다시 enterCharactername으로 넘어감  



def starting_location(state: GameSessionState)-> GameSessionState:
    """선택한 종족에 따라 시작하는 마을이 선택되었음을 알리고 그 마을을 상태값에 저장"""
    old_character_state = state["character_state"]
    updated_character_state = {
        **old_character_state,
        "location_type": "village",
        "location": "스톤브릿지"
    }
    
    return {
        "character_state" : updated_character_state
    }

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
    character_state = state.get("character_state",{})
    selected_race = character_state.get("race","")
    selected_class = character_state.get("profession","")
    race_status = db.get_status_by_race(selected_race)
    class_status = db.get_status_by_class(selected_class)
    
    result_status = {}
    for key in race_status:
        if key in class_status:
            result_status[key] = race_status[key] + class_status[key]
    
    result_status["current_hp"] = result_status["base_hp"]
    
    old_character_state = state["character_state"]
    updated_character_state = {
        **old_character_state,
        "status": result_status,
        "attack_item": "long_sword",
        "defense_item": "leather_jacket"
    }

    return {
        "character_state": updated_character_state
    }



def dive_into_game(state: GameSessionState)-> GameSessionState:
    """ CharacterState와 Status,위치를 알려주고 게임을 시작한다는 사인을 줌"""
    character = state["character_state"]
    prompt_data = {
        "character_name": character["name"],
        "character_race": character["race"].value if hasattr(character["race"], 'value') else str(character["race"]),
        "character_profession": character["profession"].value if hasattr(character["profession"], 'value') else str(character["profession"]),
        "location": character["location"],
        "location_type": character["location_type"],
        "current_hp": character["status"]["current_hp"],
        "base_hp": character["status"]["base_hp"],
        "attack_item": character["attack_item"],
        "defense_item": character["defense_item"],
        "game_phase": state["game_phase"].value if hasattr(state["game_phase"], 'value') else str(state["game_phase"]),
        "context": state["game_context"]
    }

    chain = GAME_START_PROMPT | ChatModel

    response = chain.invoke(prompt_data)
    print(response.content,flush=True)

    return {
        "system_messages":[response.content],
        "question_time":0
    }


tools = [get_race_info, get_class_info, calculate_character_stats, list_available_options]

graph = StateGraph(GameSessionState)
# 일반적으로 사용되는 노드
graph.add_node("get_user_input_intro", get_user_input_node)
graph.add_node("get_user_input_exp", get_user_input_node)
graph.add_node("get_user_input_race", get_user_input_node)
graph.add_node("get_user_input_class", get_user_input_node)
graph.add_node("get_user_input_name", get_user_input_node)

graph.add_node("validate_normal_user_input", validate_user_input_node)
# 게임에 대한 전반적인 설명
graph.add_node("introduction", introduce_background_node)
graph.add_node("reset_question_time_intro",reset_question_time_node)
graph.add_node("reset_question_time_exp", reset_question_time_node)
graph.add_node("explanation", explain_game_condition_node)
# 캐릭터 종족 선택
graph.add_node("explain_race", explain_race)
graph.add_node("race_choice_analysis", race_choice_analysis)
graph.add_node("race_router", race_choice_router)
graph.add_node("race_fix", race_fix)
# 캐릭터 직업 선택
graph.add_node("explain_class", explain_class)
graph.add_node("class_choice_analysis",class_choice_analysis)
graph.add_node("class_router",class_choice_router)
graph.add_node("class_fix",class_fix)
# 캐릭터 이름입력
graph.add_node("name_input_guidance", enter_character_name)
graph.add_node("validate_character_name",validate_character_name_router)
graph.add_node("extract_and_set_character_name", extract_character_name_node)

# 게임 시작 직전 설정 적용 및 사용자에게 알려주기 
graph.add_node("starting_location", starting_location)
graph.add_node("initial_status_items", initial_status_items)
graph.add_node("dive_into_game", dive_into_game)

graph.add_edge(START, "introduction")
graph.add_edge("introduction", "get_user_input_intro")
graph.add_conditional_edges(
    "get_user_input_intro",
    question_left_router,
    {
        "again": "introduction",
        "exit": "reset_question_time_intro"
    }
)
graph.add_edge("reset_question_time_intro","explanation")
graph.add_edge("explanation","get_user_input_exp")
graph.add_conditional_edges(
    "get_user_input_exp",
    question_left_router,
    {
        "again": "explanation",
        "exit": "reset_question_time_exp"
    }
)
graph.add_edge("reset_question_time_exp", "explain_race")
graph.add_edge("explain_race","get_user_input_race")
graph.add_edge("get_user_input_race", "race_choice_analysis")
graph.add_conditional_edges(
    "race_choice_analysis",
    race_choice_router,
    {
        "again": "explain_race",
        "exit": "race_fix"
    }
)
graph.add_edge("race_fix","explain_class")
graph.add_edge("explain_class", "get_user_input_class")
graph.add_edge("get_user_input_class", "class_choice_analysis")
graph.add_conditional_edges(
    "class_choice_analysis",
    class_choice_router,
    {
        "again": "explain_class",
        "exit": "class_fix"
    }
)
graph.add_edge("class_fix", "name_input_guidance")
graph.add_edge("name_input_guidance", "get_user_input_name")
graph.add_conditional_edges(
    "get_user_input_name",
    validate_character_name_router,
    {
        "again": "name_input_guidance",
        "exit": "extract_and_set_character_name"
    }
) 
               
graph.add_edge("extract_and_set_character_name","starting_location")
graph.add_edge("starting_location","initial_status_items" )
graph.add_edge("initial_status_items", "dive_into_game")
graph.add_edge("dive_into_game", END)


result_graph = graph.compile()


def test_intro():
    # 초기 state 준비
    initial_state = {
        "messages": [],
        "system_messages": [],
        "character_state": {
            "name": "",
            "race": "",
            "profession": "",
            "status": {},
            "location_type": "",
            "location": "",
            "attack_item": "",
            "defense_item": ""
        },
        "game_phase": GamePhase.introduction,
        "game_context": [],
        "story_summary": "",
        "question_time": 0,
        "cache_box": {}
    }
    
    try:
        result = result_graph.invoke(initial_state)
        print("Graph execution completed successfully! \n ", flush=True)
        return result
    except Exception as e:
        print(f"Error during graph execution: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None 

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