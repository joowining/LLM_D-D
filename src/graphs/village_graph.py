
from states.GameSession import GameSessionState 
from langgraph.graph import StateGraph,START, END

from graphs.util_nodes import get_user_input_node

# graph 시각화 내용
from IPython.display import Image, display
from PIL import Image as PILImage
import io

## node 정의 
def village_basic_question(state: GameSessionState) -> GameSessionState:
    pass

def basic_question_analysis_router(state: GameSessionState) -> str:
    pass

def describe_about_village(state: GameSessionState) -> GameSessionState:
    pass

def talking_npc_choice_analysis(state: GameSessionState) -> str:
    pass

def talking_like_npc(state: GameSessionState) -> GameSessionState:
    pass


def go_to_dungeon(state: GameSessionState) -> GameSessionState:
    pass

def answer_to_other_question(state: GameSessionState) -> GameSessionState:
    pass

##########

graph = StateGraph(GameSessionState)

## node 구성
# 기본 질문 노드 및 분석
graph.add_node("basic_question", village_basic_question)
graph.add_node("basic_question_input", get_user_input_node)
graph.add_node("describe_village", describe_about_village)
graph.add_node("npc_choice_input", get_user_input_node)
graph.add_node("talking_npc_choice_analysis",talking_npc_choice_analysis)
graph.add_node("talking_like_npc", talking_like_npc)
graph.add_node("answer_to_other", answer_to_other_question)


# 던전으로 빠지기
graph.add_node("go_to_dungeon", go_to_dungeon)


graph.add_edge(START, "basic_question")
graph.add_edge("basic_question", "basic_question_input")
graph.add_conditional_edges(
    "basic_question_input",
    basic_question_analysis_router,
    {
        "LOOKAROUND": "describe_village",
        "TALKING": "npc_choice_input",
        "GOTODUNGEON": "go_to_dungeon",
        "OTHER": "answer_to_other"
    }
)
graph.add_edge("describe_village", "basic_question")
graph.add_edge("answer_to_other", "basic_question")
graph.add_edge("npc_choice_input","talking_npc_choice_analysis")
graph.add_edge("talking_npc_choice_analysis","talking_like_npc")
graph.add_edge("talking_like_npc","basic_question")
graph.add_edge("go_to_dungeon",END)
    

result_village_graph = graph.compile()

def village_graph(initial_state: GameSessionState): 
    try:
        result = result_village_graph.invoke(initial_state)
        return result
    except Exception as e:
        print(f"Error during graph execution: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None 


if __name__== "__main__":
    try:
        png_graph = result_village_graph.get_graph().draw_mermaid_png()
        image = PILImage.open(io.BytesIO(png_graph))
        image.save("./village_langgraph.png")
    except Exception as e:
        print(f"PNG시각화 오류 :{e}")