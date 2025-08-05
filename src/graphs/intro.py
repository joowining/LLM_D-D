from langgraph.graph import StateGraph, START, END
from llm.llm_setting import ChatModel, LLM
from states.GameSession import GameSessionState
from enums.phase import GamePhase

# graph 시각화용 패키지
from IPython.display import Image, display

from prompts.intro_prompt import intro_script, basic_game_script,create_intro_prompt, create_basic_game_rule_prompt
from utils.intent_analysis import classify_intent
from util_node import get_user_input_node

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


"""
핵심 내용:

인간: 균형잡힌 능력, 적응력이 뛰어남, 모든 직업과 잘 어울림
엘프: 마법 친화적, 높은 지능과 민첩성, 자연과의 교감 능력
늑대인간: 강력한 물리적 능력, 변신 능력, 야생 생존 본능
야만인: 압도적인 힘과 체력, 분노 상태 진입 가능, 원시적 전투 본능
드워프: 뛰어난 제작 능력, 높은 체력, 지하 환경 적응력
각 종족별 특수 능력과 시작 지역 미리 언급
"""
def choose_race(state: GameSessionState)-> GameSessionState:
    """사용자에게 게임 내에서 선택할 수 있는 종족을 설명하고 하나만 고르도록 유도"""

    return state

def question_about_race(state: GameSessionState):
    """선택할 수 있는 종족이 있는지 질문"""
    intent = " "

    if intent == "POSITIVE":
        # 종족을 저장 
        return "exit"
    elif intent == "NEGATIVE":
        return "again"
    else:
        return "again"

"""
핵심 내용:

전사: 최전선 탱커, 높은 방어력과 근접 공격력
무술가: 민첩한 격투가, 내공을 이용한 특수 기술
성기사: 신성한 힘의 수호자, 치유와 보호 마법
사냥꾼: 원거리 전문가, 자연 마법과 추적 능력
도적: 은밀함의 달인, 함정 해제와 급소 공격
바드: 다재다능한 지원가, 음악 마법과 사회적 능력
사제: 치유 전문가, 언데드 퇴치와 신성 마법
흑마법사: 강력한 어둠 마법, 저주와 악마 소환
마법사: 원소 마법의 달인, 높은 화력의 범위 공격
"""
def choose_class(state: GameSessionState) -> GameSessionState:
    """사용자에게 게임 내에서 선택할 수 있는 직업에 대해 설명하고 하나만 고르도록 유도"""

    return state

def question_about_class(state: GameSessionState):
    """선택한 직업이 있는지 질문"""
    intent = " "

    if intent == "POSITIVE":
        # 직업을 저장 

        return "exit"
    elif intent == "NEGATIVE":
        return "again"
    else:
        return "again"

"""
종족별 시작 마을 매칭:

인간 → 스톤브릿지 (상업 중심 마을)
엘프 → 실버리프 (숲속의 엘프 마을)
늑대인간 → 울프헤이븐 (산간 부족 마을)
야만인 → 아이언클로 (험준한 고원 정착지)
드워프 → 해머홀 (지하 광산 도시)


각 마을의 특색: 지리적 위치, 주요 건물, 특산품, 주민 성향
마을의 현재 상황: 어둠의 영향으로 인한 문제점들 암시
"""
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

"""
핵심 내용:

캐릭터 종합 정리: 선택한 종족, 직업, 능력치, 장비 요약
시작 마을 상황 브리핑: 현재 마을에서 일어나고 있는 사건들
첫 번째 퀘스트 암시: "마을 사람들이 수상한 움직임을 목격했다는데..."
게임 시작 선언: "당신의 모험이 지금 시작됩니다!"
분위기 조성: 긴장감과 기대감을 높이는 서술
다음 단계 예고: "곧 여관 주인이 다가와 긴급한 도움을 요청할 것입니다"
"""
def dive_into_game(state: GameSessionState)-> GameSessionState:
    """ 현재까지 선택한 내용에 대해 알려주고 게임을 시작한다는 사인을 줌  """
    return state


graph = StateGraph(GameSessionState)
graph.add_node("introduction", introduce_background_node)
graph.add_node("reset_question_time",reset_question_time_node)
graph.add_node("user_input", get_user_input_node)
graph.add_node("question_router",question_left_router)
graph.add_node("explanation", explain_game_condition_node)
graph.add_node("choose_race", choose_race)
graph.add_node("choose_class", choose_class)
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

graph.add_conditional_edges(
    "choose_race",
    question_about_race,
    {
        "again": "choose_race",
        "exit": "choose_class"
    }
)
graph.add_conditional_edges(
    "choose_class",
    question_about_class,
    {
        "again": "choose_class",
        "exit": "starting_location"
    }
)
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