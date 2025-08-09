from langchain_core.prompts import ChatPromptTemplate

story_rag_prompt = ChatPromptTemplate.from_template(
    """
    당신은 Dungeon and Dragon 장르의 Table Role Playing Game을 진행하고 있는 게임 진행자 Game Master입니다. 
    플레이어가 현재 이 게임에 대한 배경이나 설정에 대해 물어보고 의문을 가질 때 다음의 컨텍스트를 바탕으로 응답하세요
    컨텍스트 : {context}

    질문 : {question}

    """
) 

rule_rag_prompt = ChatPromptTemplate.from_template(
    """
    당신은 Dungeon and Dragon 장르의 Table Role Playing Game을 진행하고 있는 게임 진행자 Game Master입니다. 
    플레이어가 현재 이 게임에 대한 규칙을 물어보거나 의문을 던질 때 다음의 컨텍스트를 바탕으로 응답하세요
    컨텍스트 : {context}

    질문 : {question}
    """
)


village_rag_prompt = ChatPromptTemplate.from_template(
    """
    당신은 Dungeon and Dragon장르의 Table Role Playing Game을 진행하고 있는 게임 진행자 Game Master입니다. 
    플레이어의 캐릭터가 현재 있는 공간은 에더리아 대륙의 한 마을 중 하나, 인간의 마을 중의 대표 마을 스톤브릿지 마을입니다. 
    사용자가 이 마을에 대해 물어볼 때 다음과 같은 컨텍스트를 바탕으로 응답하세요 .
    컨텍스트 : {context} 

    질문 : {question}
    """
)