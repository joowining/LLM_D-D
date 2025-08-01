from typing import TypedDict, List, Literal
from typing_extensions import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
import random

# ========== 기본 상태 정의 ==========

class GameState(TypedDict):
    messages: Annotated[List, add_messages]
    current_step: str
    user_input: str
    counter: int
    game_phase: str
    validation_attempts: int
    user_choice: str

# ========== 1. CONDITIONAL EDGES (조건부 엣지) ==========

def conditional_router(state: GameState) -> str:
    """
    조건부 라우터 함수
    - state를 받아서 다음 노드명을 문자열로 반환
    - 여러 조건에 따라 다른 경로로 분기
    """
    user_input = state.get("user_input", "").lower().strip()
    current_step = state.get("current_step", "")
    
    # 현재 단계에 따른 조건부 분기
    if current_step == "menu":
        if "게임" in user_input or "play" in user_input:
            return "start_game"
        elif "설정" in user_input or "setting" in user_input:
            return "settings"
        elif "종료" in user_input or "quit" in user_input:
            return "end_game"
        else:
            return "invalid_input"
    
    elif current_step == "game":
        if "전투" in user_input or "fight" in user_input:
            return "combat"
        elif "탐험" in user_input or "explore" in user_input:
            return "exploration"
        elif "인벤토리" in user_input or "inventory" in user_input:
            return "inventory"
        elif "메뉴" in user_input or "menu" in user_input:
            return "main_menu"
        else:
            return "invalid_action"
    
    # 기본값
    return "main_menu"

def multi_condition_router(state: GameState) -> str:
    """
    복합 조건을 사용하는 라우터
    """
    counter = state.get("counter", 0)
    attempts = state.get("validation_attempts", 0)
    user_input = state.get("user_input", "")
    
    # 여러 조건을 동시에 체크
    if attempts >= 3:
        return "too_many_attempts"
    elif counter >= 10:
        return "max_counter_reached"
    elif not user_input:
        return "no_input"
    elif user_input.isdigit():
        num = int(user_input)
        if num > 50:
            return "high_number"
        elif num < 10:
            return "low_number"
        else:
            return "medium_number"
    else:
        return "text_input"

def probability_router(state: GameState) -> str:
    """
    확률 기반 라우터 (랜덤 이벤트)
    """
    rand_num = random.randint(1, 100)
    
    if rand_num <= 10:  # 10% 확률
        return "rare_event"
    elif rand_num <= 30:  # 20% 확률
        return "uncommon_event"
    elif rand_num <= 70:  # 40% 확률
        return "common_event"
    else:  # 30% 확률
        return "normal_event"

# ========== 2. LOOP EDGES (루프 엣지) ==========

def loop_condition(state: GameState) -> str:
    """
    루프 조건을 판단하는 함수
    - 특정 조건이 만족될 때까지 같은 노드를 반복
    """
    counter = state.get("counter", 0)
    user_input = state.get("user_input", "").lower()
    
    # 종료 조건들
    if "종료" in user_input or "quit" in user_input:
        return "exit_loop"
    elif counter >= 5:
        return "max_iterations"
    elif user_input == "완료":
        return "task_completed"
    else:
        return "continue_loop"  # 루프 계속

def validation_loop_condition(state: GameState) -> str:
    """
    입력 검증을 위한 루프 조건
    """
    user_input = state.get("user_input", "")
    attempts = state.get("validation_attempts", 0)
    
    # 올바른 입력 형식 체크
    valid_inputs = ["yes", "no", "y", "n", "예", "아니오"]
    
    if attempts >= 3:
        return "max_attempts_reached"
    elif user_input.lower() in valid_inputs:
        return "valid_input"
    else:
        return "invalid_input_retry"

def game_loop_condition(state: GameState) -> str:
    """
    게임 루프 조건 (턴 기반 게임)
    """
    game_phase = state.get("game_phase", "")
    user_choice = state.get("user_choice", "")
    
    if game_phase == "game_over":
        return "end_game"
    elif user_choice == "새게임":
        return "restart_game"
    elif user_choice == "계속":
        return "continue_game"
    else:
        return "wait_for_input"

# ========== 노드 함수들 ==========

def main_menu_node(state: GameState) -> GameState:
    """메인 메뉴 노드"""
    new_state = state.copy()
    new_state["messages"] = state.get("messages", []) + [
        AIMessage(content="🎮 메인 메뉴입니다. 선택해주세요:\n1. 게임 시작\n2. 설정\n3. 종료")
    ]
    new_state["current_step"] = "menu"
    return new_state

def game_loop_node(state: GameState) -> GameState:
    """게임 루프 노드 (카운터 증가)"""
    new_state = state.copy()
    counter = state.get("counter", 0) + 1
    new_state["counter"] = counter
    new_state["messages"] = state.get("messages", []) + [
        AIMessage(content=f"🔄 루프 반복 {counter}회차입니다. '종료' 또는 '완료'를 입력하면 루프가 끝납니다.")
    ]
    new_state["current_step"] = "loop"
    return new_state

def validation_node(state: GameState) -> GameState:
    """입력 검증 노드"""
    new_state = state.copy()
    attempts = state.get("validation_attempts", 0) + 1
    new_state["validation_attempts"] = attempts
    new_state["messages"] = state.get("messages", []) + [
        AIMessage(content=f"❓ 올바른 입력을 해주세요 (시도 {attempts}/3): yes, no, y, n, 예, 아니오 중 하나를 입력하세요.")
    ]
    return new_state

def success_node(state: GameState) -> GameState:
    """성공 노드"""
    new_state = state.copy()
    new_state["messages"] = state.get("messages", []) + [
        AIMessage(content="✅ 성공적으로 완료되었습니다!")
    ]
    return new_state

def error_node(state: GameState) -> GameState:
    """에러 노드"""
    new_state = state.copy()
    new_state["messages"] = state.get("messages", []) + [
        AIMessage(content="❌ 오류가 발생했습니다. 다시 시도해주세요.")
    ]
    return new_state

def random_event_node(state: GameState) -> GameState:
    """랜덤 이벤트 노드"""
    events = {
        "rare_event": "🌟 전설적인 이벤트가 발생했습니다!",
        "uncommon_event": "⭐ 특별한 이벤트가 발생했습니다!",
        "common_event": "🎯 일반적인 이벤트가 발생했습니다.",
        "normal_event": "📝 평범한 하루입니다."
    }
    
    event_type = state.get("current_step", "normal_event")
    new_state = state.copy()
    new_state["messages"] = state.get("messages", []) + [
        AIMessage(content=events.get(event_type, "알 수 없는 이벤트"))
    ]
    return new_state

# ========== 그래프 생성 예시들 ==========

def create_conditional_edge_example():
    """조건부 엣지 예시 그래프"""
    
    graph = StateGraph(GameState)
    
    # 노드 추가
    graph.add_node("main_menu", main_menu_node)
    graph.add_node("start_game", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="🎮 게임을 시작합니다!")], "current_step": "game"})
    graph.add_node("settings", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="⚙️ 설정 메뉴입니다.")], "current_step": "settings"})
    graph.add_node("end_game", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="👋 게임을 종료합니다.")]})
    graph.add_node("invalid_input", error_node)
    
    # 시작점
    graph.add_edge(START, "main_menu")
    
    # 조건부 엣지 추가
    graph.add_conditional_edges(
        "main_menu",           # 시작 노드
        conditional_router,    # 라우터 함수
        {                      # 매핑 딕셔너리
            "start_game": "start_game",
            "settings": "settings", 
            "end_game": "end_game",
            "invalid_input": "invalid_input"
        }
    )
    
    # 종료 엣지들
    graph.add_edge("end_game", END)
    graph.add_edge("start_game", END)
    graph.add_edge("settings", "main_menu")  # 설정 후 메인 메뉴로
    graph.add_edge("invalid_input", "main_menu")  # 에러 후 메인 메뉴로
    
    return graph.compile()

def create_loop_edge_example():
    """루프 엣지 예시 그래프"""
    
    graph = StateGraph(GameState)
    
    # 노드 추가
    graph.add_node("start_loop", lambda s: {**s, "messages": [AIMessage(content="🔄 루프를 시작합니다.")], "counter": 0})
    graph.add_node("loop_body", game_loop_node)
    graph.add_node("loop_exit", success_node)
    graph.add_node("max_reached", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="🔚 최대 반복 횟수에 도달했습니다.")]})
    
    # 시작
    graph.add_edge(START, "start_loop")
    graph.add_edge("start_loop", "loop_body")
    
    # 루프 조건부 엣지
    graph.add_conditional_edges(
        "loop_body",
        loop_condition,
        {
            "continue_loop": "loop_body",      # 자기 자신으로 루프
            "exit_loop": "loop_exit",          # 루프 탈출
            "max_iterations": "max_reached",   # 최대 반복 도달
            "task_completed": "loop_exit"      # 작업 완료
        }
    )
    
    # 종료
    graph.add_edge("loop_exit", END)
    graph.add_edge("max_reached", END)
    
    return graph.compile()

def create_validation_loop_example():
    """입력 검증 루프 예시"""
    
    graph = StateGraph(GameState)
    
    # 노드 추가
    graph.add_node("ask_input", lambda s: {**s, "messages": [AIMessage(content="❓ yes 또는 no로 답변해주세요:")], "validation_attempts": 0})
    graph.add_node("validate", validation_node)
    graph.add_node("valid_response", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="✅ 올바른 입력입니다!")]})
    graph.add_node("too_many_attempts", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="❌ 시도 횟수를 초과했습니다.")]})
    
    # 시작
    graph.add_edge(START, "ask_input")
    graph.add_edge("ask_input", "validate")
    
    # 검증 루프
    graph.add_conditional_edges(
        "validate",
        validation_loop_condition,
        {
            "valid_input": "valid_response",        # 올바른 입력시 성공
            "invalid_input_retry": "validate",      # 잘못된 입력시 다시 검증
            "max_attempts_reached": "too_many_attempts"  # 최대 시도 초과
        }
    )
    
    # 종료
    graph.add_edge("valid_response", END)
    graph.add_edge("too_many_attempts", END)
    
    return graph.compile()

def create_complex_flow_example():
    """복잡한 플로우 예시 (조건부 + 루프 조합)"""
    
    graph = StateGraph(GameState)
    
    # 노드들
    graph.add_node("entry", lambda s: {**s, "messages": [AIMessage(content="🚀 복잡한 플로우 시작")], "counter": 0})
    graph.add_node("process_input", lambda s: {**s, "counter": s.get("counter", 0) + 1})
    graph.add_node("high_number", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="📈 큰 숫자입니다!")]})
    graph.add_node("low_number", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="📉 작은 숫자입니다!")]})
    graph.add_node("medium_number", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="📊 적당한 숫자입니다!")]})
    graph.add_node("text_input", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="📝 텍스트 입력입니다!")]})
    graph.add_node("no_input", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="❓ 입력이 없습니다!")]})
    graph.add_node("too_many_attempts", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="⏰ 너무 많은 시도!")]})
    graph.add_node("max_counter", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="🔢 카운터 최대값 도달!")]})
    
    # 시작
    graph.add_edge(START, "entry")
    graph.add_edge("entry", "process_input")
    
    # 복합 조건부 엣지
    graph.add_conditional_edges(
        "process_input",
        multi_condition_router,
        {
            "high_number": "high_number",
            "low_number": "low_number", 
            "medium_number": "medium_number",
            "text_input": "text_input",
            "no_input": "no_input",
            "too_many_attempts": "too_many_attempts",
            "max_counter_reached": "max_counter"
        }
    )
    
    # 대부분의 노드에서 다시 입력 처리로 루프
    for node in ["high_number", "low_number", "medium_number", "text_input", "no_input"]:
        graph.add_edge(node, "process_input")
    
    # 종료 조건들
    graph.add_edge("too_many_attempts", END)
    graph.add_edge("max_counter", END)
    
    return graph.compile()

def create_random_event_example():
    """확률 기반 이벤트 예시"""
    
    graph = StateGraph(GameState)
    
    # 노드들
    graph.add_node("spin_wheel", lambda s: {**s, "messages": [AIMessage(content="🎰 운명의 룰렛을 돌립니다...")]})
    graph.add_node("rare_event", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="🌟 전설적! (10% 확률)")], "current_step": "rare_event"})
    graph.add_node("uncommon_event", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="⭐ 희귀! (20% 확률)")], "current_step": "uncommon_event"})
    graph.add_node("common_event", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="🎯 일반 (40% 확률)")], "current_step": "common_event"})
    graph.add_node("normal_event", lambda s: {**s, "messages": s.get("messages", []) + [AIMessage(content="📝 평범 (30% 확률)")], "current_step": "normal_event"})
    graph.add_node("event_result", random_event_node)
    
    # 플로우
    graph.add_edge(START, "spin_wheel")
    
    # 확률 기반 분기
    graph.add_conditional_edges(
        "spin_wheel",
        probability_router,
        {
            "rare_event": "rare_event",
            "uncommon_event": "uncommon_event", 
            "common_event": "common_event",
            "normal_event": "normal_event"
        }
    )
    
    # 모든 이벤트에서 결과로
    for event in ["rare_event", "uncommon_event", "common_event", "normal_event"]:
        graph.add_edge(event, "event_result")
    
    graph.add_edge("event_result", END)
    
    return graph.compile()

# ========== 사용 예시 ==========

def test_conditional_edges():
    """조건부 엣지 테스트"""
    print("=== 조건부 엣지 테스트 ===")
    
    app = create_conditional_edge_example()
    
    test_inputs = ["게임", "설정", "종료", "잘못된입력"]
    
    for user_input in test_inputs:
        print(f"\n입력: '{user_input}'")
        
        initial_state = {
            "messages": [],
            "current_step": "",
            "user_input": user_input,
            "counter": 0,
            "game_phase": "",
            "validation_attempts": 0,
            "user_choice": ""
        }
        
        result = app.invoke(initial_state)
        
        for message in result["messages"]:
            if hasattr(message, 'content'):
                print(f"응답: {message.content}")

def test_loop_edges():
    """루프 엣지 테스트"""
    print("\n=== 루프 엣지 테스트 ===")
    
    app = create_loop_edge_example()
    
    # 여러 번 실행하여 루프 확인
    test_inputs = ["계속", "계속", "계속", "종료"]
    
    state = {
        "messages": [],
        "current_step": "",
        "user_input": "",
        "counter": 0,
        "game_phase": "",
        "validation_attempts": 0,
        "user_choice": ""
    }
    
    for user_input in test_inputs:
        print(f"\n입력: '{user_input}'")
        state["user_input"] = user_input
        
        result = app.invoke(state)
        state = result  # 상태 유지
        
        print(f"카운터: {result.get('counter', 0)}")
        if result.get("messages"):
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                print(f"응답: {last_message.content}")

def test_validation_loop():
    """검증 루프 테스트"""
    print("\n=== 검증 루프 테스트 ===")
    
    app = create_validation_loop_example()
    
    test_inputs = ["maybe", "perhaps", "yes"]
    
    state = {
        "messages": [],
        "current_step": "",
        "user_input": "",
        "counter": 0,
        "game_phase": "",
        "validation_attempts": 0,
        "user_choice": ""
    }
    
    for user_input in test_inputs:
        print(f"\n입력: '{user_input}'")
        state["user_input"] = user_input
        
        result = app.invoke(state)
        state = result
        
        print(f"검증 시도: {result.get('validation_attempts', 0)}")
        if result.get("messages"):
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                print(f"응답: {last_message.content}")

if __name__ == "__main__":
    test_conditional_edges()
    test_loop_edges()
    test_validation_loop()
    
    print("\n=== 확률 기반 이벤트 테스트 ===")
    random_app = create_random_event_example()
    
    for i in range(5):
        print(f"\n{i+1}번째 실행:")
        result = random_app.invoke({
            "messages": [],
            "current_step": "",
            "user_input": "",
            "counter": 0,
            "game_phase": "",
            "validation_attempts": 0,
            "user_choice": ""
        })
        
        for message in result["messages"]:
            if hasattr(message, 'content'):
                print(f"결과: {message.content}")