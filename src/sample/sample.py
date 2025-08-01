from typing import TypedDict,Annotated, List
from pydantic import BaseModel
from enum import Enum

from IPython.display import Image, display

# Langchain
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool

# Langgraph
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START, END
from langgraph.prebuilt import ToolNode

class RaceEnum(str,Enum):
    HUMAN = "인간"
    ELF = "엘프"
    WAREWOLF = "늑대인간"
    BARBARIAN = "야만인"
    DWARF = "드워프"

class ClassEnum(str, Enum):
    WARRIOR = "전사"
    MONK = "무도가"
    PALADIN = "성기사"
    HUNTER = "사냥꾼"
    ROGUE = "도적"
    BARD = "바드"
    PRIEST = "사제"
    WALOCK = "흑마법사"
    WIZARD = "마법사"
    



class UserState(TypedDict):
    messages: Annotated[List, add_messages]
    selected_race: str
    selected_class: str

tools = []

llm = ChatOllama(model="exaone3.5:latest").bind_tools(tools)

races = [race.name for race in RaceEnum]
race_str = ','.join(races)
 

def choose_races(state: UserState)-> UserState:
    """사용자에게 선택할 종족을 제안하고 한가지를 선택하도록 유도"""
    prompt_template = PromptTemplate(
        input_variables=["choice","options"],
        template="""
            당신은 Dungeon and Dragon장르의 Table Role Playing Game을 진행하고
            사용자의 입력에 따라 게임의 진행상황과 개연성에 맞게 응답할 책임이 있는 Game Master입니다.

            지금은 {choice}를 해야하는 상황입니다.
            사용자에게는 다음과 같은 선택지가 있습니다:
            {options}

            위 내용을 바탕으로 사용자에게 상황을 설명하고 제안해주세요.
        """
    )
    formatted_prompt = prompt_template.format(
        choice="종족 선택",
        options=race_str
    )
    response = llm.invoke(formatted_prompt)

    new_state = state.copy()
    new_state["messages"] = state.get("messages",[]) + [AIMessage(content=response.content)]

    return new_state

def process_user_input(state: UserState) -> UserState:
    """사용자의 입력을 처리하고 검증"""

    user_messages = [msg for msg in state.get("messages",[])]

    if user_messages:
        user_input = user_messages[-1].content.upper()

        # 입력 검증
        if user_input in [race.name for race in RaceEnum]:
            selected_race_value = RaceEnum[user_input].name
            response_text = f"훌륭한 선택입니다! {selected_race_value}을(를) 선택하셨군요. 이제 다음 선택지를 제안하겠습니다."
        else:
            response_text = f"올바르지 않은 선택입니다. 다음 중에서 선택해주세요 {race_str}"
    else:
        response_text=  "입력 받지 못했습니다. "

    ai_response = llm.invoke(f"Game Master로서 다음 내용을 자연스럽게 전달해주세요 : {response_text}")

    new_state = state.copy()
    new_state["messages"] = state.get("messages",[]) + [ai_response]
    if user_input in [race.name for race in RaceEnum]:
        new_state["selected_race"] = RaceEnum[user_input].value
    
    return new_state



myGraph = StateGraph(UserState)

myGraph.add_node("choose_races",choose_races)
myGraph.add_node("process_input", process_user_input)

myGraph.add_edge(START, "choose_races")
myGraph.add_edge("choose_races", "process_input")
myGraph.add_edge("choose_races", END)

app = myGraph.compile()

usr_input = input(f"select your race: options : {race_str}\n your input : ")

initial_state = {
    "messages": [HumanMessage(content=usr_input)],
    "selected_race":"",
    "selected_class":"",
}

result = app.invoke(initial_state)

print("\n=== Game Master Response ===")
for message in result["messages"]:
    if hasattr(message, 'content'):
        print(message.content)
        print("-" * 50)

if result.get("selected_race"):
    print(f"Selected Race: {result["selected_race"]}")