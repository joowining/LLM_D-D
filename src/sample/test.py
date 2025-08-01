from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

# 초기 상태 구조 정의
state = {
    "history": [],
    "user_input": None
}

# 사용자 입력 받기 노드
def get_user_input(state):
    print("👉 사용자 입력을 기다립니다:")
    user_input = input("> ")
    state["user_input"] = user_input
    state["history"].append(user_input)
    return state

# 조건 판단 노드
def judge(state):
    if state["user_input"].lower() == "done":
        return "done"
    else:
        return "continue"

# 요약 노드 (여기서는 간단히 join)
def summarize(state):
    summary = "전체 입력 요약:\n" + "\n".join(state["history"])
    print(summary)
    return state

# LangGraph 구성
builder = StateGraph()

builder.add_node("input", RunnableLambda(get_user_input))
builder.add_node("judge", RunnableLambda(judge))
builder.add_node("summarize", RunnableLambda(summarize))

builder.set_entry_point("input")
builder.add_edge("input", "judge")
builder.add_conditional_edges(
    "judge",
    {
        "continue": "input",
        "done": "summarize",
    }
)
builder.add_edge("summarize", END)

graph = builder.compile()

# 실행
graph.invoke(state)
