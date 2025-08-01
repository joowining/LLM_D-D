from langgraph.graph import StateGraph, START, END
#from llm.llm_setting import ChatModel
from states.GameSession import GameSessionState

# graph 시각화
from IPython.display import Image, display


def introduce_background_node(state: GameSessionState)-> GameSessionState:
    """현재 게임에 대한 배경을 설명"""
    
    return state


def explain_game_condition_node(state: GameSessionState)-> GameSessionState:
    """게임을 플레이하는 방법과 클리어 조건과 게임 오버 조건 설명"""

    return state

def question_left_router(state: GameSessionState):
    """사용자에게 현재 섹션에 대하여 질문이 남아 있는지 확인"""
    intent =""
    
    if intent == "POSITIVE":
        return "again"
    elif intent == "NEGATIVE":
        return  "exit"
    else:
        return "again"

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

def starting_location(state: GameSessionState)-> GameSessionState:
    """선택한 종족에 따라 시작하는 마을이 선택되었음을 알리고 그 마을을 상태값에 저장"""
    return state

def initial_status_items(state: GameSessionState) -> GameSessionState:
    """ 선택한 종족과 직업에 따라 보너스 스테이터스와 초기장비를 지급하고 그 내용을 상태값에 저장"""

    return state

def dive_into_game(state: GameSessionState)-> GameSessionState:
    """ 현재까지 선택한 내용에 대해 알려주고 게임을 시작한다는 사인을 줌  """
    return state


graph = StateGraph(GameSessionState)
graph.add_node("introduction", introduce_background_node)
graph.add_node("explanation", explain_game_condition_node)
graph.add_node("choose_race", choose_race)
graph.add_node("choose_class", choose_class)
graph.add_node("starting_location", starting_location)
graph.add_node("initial_status_items", initial_status_items)
graph.add_node("dive_into_game", dive_into_game)

graph.add_edge(START, "introduction")
graph.add_conditional_edges(
    "introduction",
    question_left_router,
    {
        "again": "introduction",
        "exit": "explanation"
    }
)
graph.add_conditional_edges(
    "explanation",
    question_left_router,
    {
        "again": "explanation",
        "exit": "choose_race"
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

if __name__ == "__main__":
    try:
        png_data = result_graph.get_graph().draw_mermaid_png()
        with open("intro_graph.png", "wb") as f:
            f.write(png_data)
        print("intro graph is saved as intro_graph.png")
    except Exception as e:
        print(f" PNG save failed: {e}")
        print("ASCII TEXT visualization")
        print(result_graph.get_graph().draw_ascii())