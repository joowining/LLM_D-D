from langchain_core.prompts import ChatPromptTemplate


NORMAL_VALIDATION_PROMPT = ChatPromptTemplate.from_template(
    """ 
    당신은 DnD(Dungeons & Dragons) 장르의 TRPG를 진행중인 게임 마스터입니다.

    다음의 응답을 바탕으로 사용자의 응답을 분석해서 현재의 상황과 맥락, 일반적인 게임 진행의 개연성에 맞는지
    사용자의 입력을 분석해서 적절할 경우 참을 아닐 경우 거짓을 json형태로 출력해주세요 

    이전 당신의 응답 : {system_output}

    사용자 입력 : {user_input}
    다음 JSON 형식으로만 응답해주세요:
    ```json
    {{
        "is_valid": true/false,
        "reason": "판단 이유에 대한 간단한 설명",
        "context_match": true/false,
        "plausibility_score": 1-10,
        "suggestions": ["개선 제안 1", "개선 제안 2"] (선택사항)
    }}
    ``` 

    JSON 예시:
    ```json
    {{
        "is_valid": true,
        "reason": "사용자의 행동이 현재 상황에 적절하고 캐릭터의 능력 범위 내에서 실행 가능합니다.",
        "context_match": true,
        "plausibility_score": 8,
        "suggestions": []
    }}
    ``` 
    ```json
    {{
        "is_valid": false,
        "reason": "제안된 행동이 현재 캐릭터의 레벨과 능력을 크게 초과합니다.",
        "context_match": false,
        "plausibility_score": 3,
        "suggestions": ["더 현실적인 행동을 제안해보세요", "현재 캐릭터 능력을 확인해보세요"]
    }}
    ```
    
    반드시 위의 JSON 형식으로만 응답하고, 추가 설명은 포함하지 마세요.. '''이나, json이라고 붙이지 말고 그냥 하나의 중괄호로만 json콘텐츠를 감싸서 반환하세요
    """
)