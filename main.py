# 패키지 목록
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama import ChatOllama


# 기본적인 LangChain과 FastAPI활용한 제일 기본적 형태의 단순 채팅 LLM DnD 서버

llm = ChatOllama(model="exaone3.5:latest", temperature=0.5)


## prompt 템플릿
prompt = ChatPromptTemplate.from_messages([
    ("system", """
         당신은 Dungeon and Dragon 장르의 TRPG 게임을 진행하는 게임 마스터입니다.\
        사용자는 게임의 플레이어이며 그들의 요청과 응답에 따라 게임을 진행하되 개연성을 고려해야합니다.\
        최초에 게임 배경과 스토리를 설명하고 직업 및 종족을 선택하게 한 뒤 마을, 던전을 소개해서 플레이어를 \
        게임의 세계에 몰입할 수 있도록 도와주세요.
        한국어로만 응답하세요. 
     """),
    ("placeholder","{chat_history}"),
    ("ai", """ 
            게임을 시작합니다. 당신은 현재 판타지 대륙에 있습니다. 다음에 할 행동이나 질문을 입력해주세요. \
            종료를 원한다면 'exit'를 입력하세요. 
    """),
    ("human", "{input}")
])

chain = prompt | llm 

store = {} 

def get_session_history(session_id: str) -> ChatMessageHistory:
    """
    세션 ID에 해당하는 메시지 히스토리를 가져오는 함수
    """
    # 실제 구현에서는 세션 ID에 해당하는 메시지 히스토리를 데이터베이스나 다른 저장소에서 가져와야 합니다.
    # 여기서는 예시로 빈 히스토리를 반환합니다.
    if session_id not in store: 
        store[session_id] = ChatMessageHistory()
    return store[session_id]


chat_with_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key = "input",
    history_messages_key = "chat_history"
)


if __name__ == "__main__":
    session_id = "1234"
    print("=== D&D TRPG 게임 시작 ===")
    
    # ✅ 시작 메시지를 직접 출력
    print("GM: 게임을 시작합니다. 당신은 현재 판타지 대륙에 있습니다. 다음에 할 행동이나 질문을 입력해주세요. 종료를 원한다면 'exit'를 입력하세요.")


    input_message = ""
    while input_message != "exit":
        input_message = input("플레이어 입력: ")
        if input_message == "exit":
            print("게임을 종료합니다.")
            break
        try: 
            response = chat_with_history.invoke(
                {"input": input_message},
                config={"configurable": {"session_id": session_id}}
            )
            print("GM: ", response.content)
            print("-" * 50)
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")