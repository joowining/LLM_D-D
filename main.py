# langchain packages
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage        
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import chain
#from langchain_core.runnables import RunnablePassthrough

model_name = "exaone3.5:latest"

llm = ChatOllama(model=model_name, temperature=0.1)

prompt = ChatPromptTemplate.from_template(
    '''
        다음 컨텍스트를 기준으로 사용자의 요청에 응답하세요. 
        스스로 판단했을 때 개연성이 떨어지는 상황에는 사용자로 하여금 개연성이 떨어지는 이유와 함께 
        요청을 다시 보내도록 응답하세요 
        컨텍스트: {context}
        사용자 요청: {question}
        응답: '''
)

chatbot = prompt | llm


if __name__ == "__main__":
    context = "당신은 Duengon and Draons 게임의 규칙과 세계관에 대해 잘 알고 있는 전문가이면서  \
        현재 이 게임을 진행하구 주관하는 게임마스터입니다. \
        사용자의 요청에 맞게 응답하고 게임을 진행할 수 있또록 응답하세요. \
        이 게임은 플레이어들이 가상의 세계에서 모험을 떠나며, 각 플레이어는 캐릭터를 생성하고 그 캐릭터의 능력치, 배경, 직업 등을 설정합니다.  \
        게임은 주로 던전 마스터(DM)라고 불리는 진행자가 이야기를 이끌어가며, 플레이어들은 DM이 제시하는 상황에 대해 행동을 결정합니다.  \
        이 게임은 주사위를 사용하여 캐릭터의 행동 \
        결과를 결정하며, 플레이어들은 협력하여 적과 싸우고, 퍼즐을 풀고, 이야기를 진행합니다.  \
        D&D는 다양한 확장판과 설정이 있으며, 각 설정마다 고유한 세계관과 규칙이 존재합니다.  \
        이 게임은 창의력과 상상력을 발휘할 수 있는 기회를 제공하며, 플레이어들은 자신의 캐릭터를 통해 다양한 역할을 경험할 수 있습니다.  \
        D&D는 협동과 전략, 그리고 이야기 전개를 중시하는 게임입니다.\
        이 게임은 플레이어들이 상호작용하며 이야기를 만들어가는 과정에서 많은 재미와 도전을 제공합니다."

    question = "게임을 시작하고 싶어, 어떤 캐릭터를 생성할 수 있고 내가 선택할 수 있는 캐릭터를 만들고 싶어 내가 선택할 수 있는 캐릭터에 대한 내용을 알려줘 "

    response = chatbot.invoke({"context":context, "question":question})  # 함수 호출
    
    print(response.content)  # 응답 출력
