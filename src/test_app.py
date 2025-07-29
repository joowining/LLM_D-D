from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import re

# D&D 게임 상태를 나타내는 열거형
class GameState(str, Enum):
    EXPLORATION = "exploration"  # 탐험 중
    COMBAT = "combat"           # 전투 중
    DIALOGUE = "dialogue"       # 대화 중
    CHOICE = "choice"          # 선택 상황
    REST = "rest"              # 휴식 중
    TOWN = "town"              # 마을/안전지대

# D&D 의도 분석 결과 모델 (간소화)
class DnDIntentAnalysis(BaseModel):
    primary_intent: str = Field(description="주요 의도")
    intent_category: str = Field(description="의도 카테고리")
    confidence: float = Field(description="신뢰도", ge=0.0, le=1.0)
    secondary_intents: List[str] = Field(description="부차적 의도들", default_factory=list)
    target: Optional[str] = Field(description="행동 대상", default=None)
    dice_roll_needed: bool = Field(description="주사위 굴림 필요 여부", default=False)
    skill_check: Optional[str] = Field(description="필요한 스킬 체크", default=None)
    risk_level: str = Field(description="위험도", default="보통")
    narrative_impact: str = Field(description="스토리 영향", default="보통")
    requires_dm_creativity: bool = Field(description="DM 창의적 해석 필요", default=False)
    game_state_change: Optional[str] = Field(description="게임 상태 변화", default=None)

class OllamaDnDIntentAnalyzer:
    def __init__(self, model_name: str = "exaone3.5:latest", ollama_base_url: str = "http://localhost:11434"):
        """
        Ollama LLM 초기화
        
        Args:
            model_name: 사용할 모델명 (llama3.1, mistral, codellama 등)
            ollama_base_url: Ollama 서버 URL
        """
        self.llm = Ollama(
            model=model_name,
            base_url=ollama_base_url,
            temperature=0.1,  # 일관성을 위해 낮은 temperature
            num_predict=512,  # 응답 길이 제한
        )
        
        # D&D 의도 카테고리 정의
        self.intent_categories = {
            "전투": [
                "전투시작", "전투행동", "전투회피", "방어", "전략수립"
            ],
            "탐험": [
                "이동", "탐색", "상호작용", "은신", "등반_수영"
            ],
            "소셜": [
                "대화", "설득", "기만", "위협", "거래", "정보수집"
            ],
            "메타": [
                "스탯확인", "스킬사용", "아이템사용", "휴식", "질문", "규칙확인"
            ],
            "결정": [
                "선택", "창의적행동", "조건부행동", "롤플레이"
            ]
        }
        
        # 간소화된 프롬프트 (로컬 LLM 최적화)
        self.analysis_prompt = PromptTemplate(
            input_variables=["user_input", "game_state", "context"],
            template="""당신은 D&D 게임 분석 AI입니다. 플레이어 입력을 분석하세요.

게임 상태: {game_state}
현재 상황: {context}
플레이어 입력: "{user_input}"

의도 카테고리:
- 전투: 전투시작, 전투행동, 전투회피, 방어, 전략수립
- 탐험: 이동, 탐색, 상호작용, 은신, 등반_수영  
- 소셜: 대화, 설득, 기만, 위협, 거래, 정보수집
- 메타: 스탯확인, 스킬사용, 아이템사용, 휴식, 질문, 규칙확인
- 결정: 선택, 창의적행동, 조건부행동, 롤플레이

다음 형식으로 정확히 응답하세요:
PRIMARY_INTENT: [주요 의도]
CATEGORY: [카테고리]
CONFIDENCE: [0.0-1.0]
SECONDARY: [부차적 의도1, 부차적 의도2]
TARGET: [대상 또는 None]
DICE_NEEDED: [true/false]
SKILL_CHECK: [스킬명 또는 None]
RISK: [낮음/보통/높음]
IMPACT: [미미/보통/중대]
CREATIVE: [true/false]
STATE_CHANGE: [새 상태 또는 None]"""
        )
        
        # LLM Chain 생성
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.analysis_prompt,
            verbose=False
        )
    
    def parse_llm_response(self, response: str) -> DnDIntentAnalysis:
        """LLM 응답을 파싱하여 구조화된 결과로 변환"""
        try:
            # 정규식으로 각 필드 추출
            patterns = {
                'primary_intent': r'PRIMARY_INTENT:\s*(.+?)(?:\n|$)',
                'category': r'CATEGORY:\s*(.+?)(?:\n|$)',
                'confidence': r'CONFIDENCE:\s*([\d.]+)',
                'secondary': r'SECONDARY:\s*(.+?)(?:\n|$)',
                'target': r'TARGET:\s*(.+?)(?:\n|$)',
                'dice_needed': r'DICE_NEEDED:\s*(true|false)',
                'skill_check': r'SKILL_CHECK:\s*(.+?)(?:\n|$)',
                'risk': r'RISK:\s*(.+?)(?:\n|$)',
                'impact': r'IMPACT:\s*(.+?)(?:\n|$)',
                'creative': r'CREATIVE:\s*(true|false)',
                'state_change': r'STATE_CHANGE:\s*(.+?)(?:\n|$)'
            }
            
            extracted = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, response, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    
                    # 데이터 타입 변환
                    if key == 'confidence':
                        extracted[key] = min(max(float(value), 0.0), 1.0)
                    elif key in ['dice_needed', 'creative']:
                        extracted[key] = value.lower() == 'true'
                    elif key == 'secondary':
                        # 리스트 파싱
                        if value and value.lower() != 'none':
                            extracted[key] = [item.strip() for item in value.split(',') if item.strip()]
                        else:
                            extracted[key] = []
                    elif key in ['target', 'skill_check', 'state_change']:
                        extracted[key] = None if value.lower() == 'none' else value
                    else:
                        extracted[key] = value
            
            # 기본값 설정
            return DnDIntentAnalysis(
                primary_intent=extracted.get('primary_intent', '질문'),
                intent_category=extracted.get('category', '메타'),
                confidence=extracted.get('confidence', 0.5),
                secondary_intents=extracted.get('secondary', []),
                target=extracted.get('target'),
                dice_roll_needed=extracted.get('dice_needed', False),
                skill_check=extracted.get('skill_check'),
                risk_level=extracted.get('risk', '보통'),
                narrative_impact=extracted.get('impact', '보통'),
                requires_dm_creativity=extracted.get('creative', False),
                game_state_change=extracted.get('state_change')
            )
            
        except Exception as e:
            print(f"응답 파싱 오류: {e}")
            print(f"원본 응답: {response}")
            # 기본값 반환
            return DnDIntentAnalysis(
                primary_intent="질문",
                intent_category="메타",
                confidence=0.5
            )
    
    def analyze_intent(self, user_input: str, game_state: GameState = GameState.EXPLORATION, 
                      context: str = "") -> DnDIntentAnalysis:
        """플레이어 입력의 의도를 분석합니다."""
        try:
            # LLM 실행
            response = self.chain.invoke(
                user_input=user_input,
                game_state=game_state.value,
                context=context if context else "일반적인 모험 상황"
            )
            
            # 응답 파싱
            analysis = self.parse_llm_response(response)
            return analysis
            
        except Exception as e:
            print(f"의도 분석 중 오류 발생: {e}")
            return DnDIntentAnalysis(
                primary_intent="질문",
                intent_category="메타",
                confidence=0.5
            )
    
    def get_prompt_template_for_intent(self, analysis: DnDIntentAnalysis) -> str:
        """분석된 의도에 따라 적절한 프롬프트 템플릿을 반환합니다."""
        intent = analysis.primary_intent
        
        templates = {
            # 전투 관련
            "전투시작": f"""전투 시작! 다음을 처리하세요:
- 이니셔티브 굴리기
- 전투 상황 묘사
- {analysis.target or '적'}의 반응 결정
위험도: {analysis.risk_level}""",
            
            "전투행동": f"""전투 행동 처리:
{"- " + analysis.skill_check + " 체크 필요" if analysis.skill_check else ""}
{"- 주사위 굴리기 필요" if analysis.dice_roll_needed else ""}
- 결과 계산 및 상황 변화 묘사""",
            
            # 탐험 관련
            "탐색": f"""탐색 행동 처리:
{"- " + analysis.skill_check + " 체크 실행" if analysis.skill_check else ""}
- 발견 요소 결정
- 환경 상세 묘사
- 위험 요소 고려
창의적 해석: {analysis.requires_dm_creativity}""",
            
            "이동": f"""이동 처리:
- 여정 묘사
- 도중 사건 고려
- 도착지 설명
스토리 영향: {analysis.narrative_impact}""",
            
            # 소셜 관련
            "대화": f"""대화 진행:
대상: {analysis.target or 'NPC'}
- NPC 성격 반영
- 자연스러운 대화 생성
- 정보/퀘스트 연결 고려""",
            
            "설득": f"""설득 시도:
{"- 설득 체크 필요" if analysis.dice_roll_needed else ""}
- NPC 반응 결정
- 성공/실패 결과 제시
위험도: {analysis.risk_level}""",
            
            # 메타게임
            "질문": "플레이어 질문에 명확하고 일관된 답변 제공",
            "스탯확인": "현재 캐릭터 상태 (HP, 스킬, 아이템 등) 정리 및 표시",
            
            # 결정
            "선택": f"""선택 처리:
- 선택 결과 적용
- 스토리 진행
- 새로운 상황 제시
상태 변화: {analysis.game_state_change or '없음'}""",
            
            "창의적행동": f"""창의적 행동 처리:
- 가능성 판단
{"- 적절한 체크 요구" if analysis.dice_roll_needed else ""}
- 창의성 보상 고려
창의적 해석 필요: {analysis.requires_dm_creativity}"""
        }
        
        return templates.get(intent, f"""일반 행동 처리:
의도: {intent} ({analysis.intent_category})
- 상황에 맞는 적절한 반응
- 게임 재미와 몰입감 유지""")

# Ollama 기반 DM 응답 생성기
class OllamaDMResponseGenerator:
    def __init__(self, model_name: str = "exaone3.5:latest", ollama_base_url: str = "http://localhost:11434"):
        self.llm = Ollama(
            model=model_name,
            base_url=ollama_base_url,
            temperature=0.7,  # 창의적 응답을 위해 높은 temperature
            num_predict=1024,  # 더 긴 응답 허용
        )
        
        self.response_prompt = PromptTemplate(
            input_variables=["guidelines", "user_input", "context", "character_info"],
            template="""당신은 숙련된 D&D 던전마스터입니다.

캐릭터: {character_info}
상황: {context}
플레이어 행동: {user_input}

처리 지침:
{guidelines}

흥미롭고 몰입감 있는 DM 응답을 해주세요. 생생한 묘사와 함께 게임을 진행하세요.

DM 응답:"""
        )
        
        self.response_chain = LLMChain(
            llm=self.llm,
            prompt=self.response_prompt,
            verbose=False
        )
    
    def generate_response(self, analysis: DnDIntentAnalysis, user_input: str, 
                         guidelines: str, context: str = "", 
                         character_info: str = "") -> str:
        """분석된 의도에 따라 DM 응답을 생성합니다."""
        try:
            response = self.response_chain.invoke(
                guidelines=guidelines,
                user_input=user_input,
                context=context or "모험 진행 중",
                character_info=character_info or "모험가"
            )
            return response.strip()
        except Exception as e:
            return f"DM 응답 생성 중 오류: {e}"

# 통합 Ollama D&D 게임 시스템
class OllamaDnDGameSystem:
    def __init__(self, model_name: str = "exaone3.5:latest", ollama_base_url: str = "http://localhost:11434"):
        self.intent_analyzer = OllamaDnDIntentAnalyzer(model_name, ollama_base_url)
        self.response_generator = OllamaDMResponseGenerator(model_name, ollama_base_url)
        self.game_state = GameState.EXPLORATION
        self.context = "모험을 시작하는 상황"
        
    def process_player_input(self, user_input: str, character_info: str = "") -> Dict[str, Any]:
        """플레이어 입력을 처리하고 DM 응답을 생성합니다."""
        
        # 1. 의도 분석
        print("🔍 의도 분석 중...")
        analysis = self.intent_analyzer.analyze_intent(
            user_input, self.game_state, self.context
        )
        
        # 2. 적절한 프롬프트 템플릿 생성
        guidelines = self.intent_analyzer.get_prompt_template_for_intent(analysis)
        
        # 3. DM 응답 생성
        print("🎭 DM 응답 생성 중...")
        dm_response = self.response_generator.generate_response(
            analysis, user_input, guidelines, self.context, character_info
        )
        
        # 4. 게임 상태 업데이트
        if analysis.game_state_change:
            try:
                new_state = GameState(analysis.game_state_change)
                self.game_state = new_state
                print(f"🔄 게임 상태 변경: {new_state.value}")
            except ValueError:
                pass
        
        return {
            "intent_analysis": analysis.model_dump(),
            "guidelines": guidelines,
            "dm_response": dm_response,
            "current_game_state": self.game_state.value,
            "dice_roll_needed": analysis.dice_roll_needed,
            "skill_check": analysis.skill_check
        }
    
    def update_context(self, new_context: str):
        """게임 컨텍스트 업데이트"""
        self.context = new_context
    
    def set_game_state(self, new_state: GameState):
        """게임 상태 수동 설정"""
        self.game_state = new_state

# 사용 예제 및 테스트
def main():
    print("🎲 Ollama D&D 게임 시스템을 시작합니다...")
    print("📝 사용 중인 모델: exaone3.5:latset")
    print("🔗 Ollama 서버: http://localhost:11434")
    print()
    
    try:
        # 게임 시스템 초기화
        game = OllamaDnDGameSystem(model_name="exaone3.5:latest")
        
        # 테스트 시나리오
        test_scenarios = [
            {
                "input": "앞에 있는 문을 자세히 조사해보겠습니다",
                "context": "어두운 던전 복도에 서 있습니다",
                "character": "레벨 3 로그, 조사 숙련"
            },
            {
                "input": "고블린을 단검으로 공격합니다!",
                "context": "고블린 2마리와 전투 중",
                "character": "레벨 2 파이터, HP 15/18"
            },
            {
                "input": "술집 주인에게 이 마을에서 일어난 이상한 일들에 대해 물어보겠습니다",
                "context": "마을 중앙의 선술집",
                "character": "레벨 1 바드, 카리스마 16"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"🎭 [시나리오 {i}]")
            print(f"플레이어: {scenario['input']}")
            print(f"상황: {scenario['context']}")
            print(f"캐릭터: {scenario['character']}")
            print()
            
            # 컨텍스트 설정
            game.update_context(scenario['context'])
            
            # 플레이어 입력 처리
            result = game.process_player_input(scenario['input'], scenario['character'])
            
            # 결과 출력
            analysis = result['intent_analysis']
            print("📊 의도 분석 결과:")
            print(f"  🎯 주요 의도: {analysis['primary_intent']} ({analysis['intent_category']})")
            print(f"  📈 신뢰도: {analysis['confidence']:.2f}")
            if analysis['dice_roll_needed']:
                print(f"  🎲 주사위 필요: {analysis['skill_check'] or '일반 체크'}")
            print(f"  ⚠️  위험도: {analysis['risk_level']}")
            print()
            
            print("🎭 DM 응답:")
            print(result['dm_response'])
            print()
            print("=" * 70)
            print()
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("💡 Ollama가 실행 중인지 확인하고, 모델이 다운로드되어 있는지 확인하세요.")
        print("   명령어: ollama pull llama3.1")

# 인터랙티브 게임 실행 함수
def run_interactive_game():
    """인터랙티브 D&D 게임 실행"""
    print("🎲 인터랙티브 D&D 게임을 시작합니다!")
    print("'quit' 입력으로 종료할 수 있습니다.")
    print()
    
    try:
        game = OllamaDnDGameSystem()
        
        # 캐릭터 설정
        character_info = input("캐릭터 정보를 입력하세요 (예: 레벨 3 위저드, HP 20/24): ")
        initial_context = input("초기 상황을 설정하세요 (예: 어두운 던전 입구): ")
        
        game.update_context(initial_context)
        print(f"\n🏁 게임이 시작됩니다! 상황: {initial_context}")
        print()
        
        while True:
            user_input = input("🗣️  행동을 입력하세요: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 게임을 종료합니다!")
                break
            
            if not user_input:
                continue
            
            print()
            result = game.process_player_input(user_input, character_info)
            
            # 간단한 분석 결과 표시
            analysis = result['intent_analysis']
            if analysis['dice_roll_needed']:
                print(f"🎲 {analysis['skill_check'] or '체크'} 굴림이 필요합니다!")
            
            print("🎭 DM:", result['dm_response'])
            print()
            
    except KeyboardInterrupt:
        print("\n👋 게임을 종료합니다!")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    print("1. 테스트 실행")
    print("2. 인터랙티브 게임")
    choice = input("선택하세요 (1 또는 2): ").strip()
    
    if choice == "2":
        run_interactive_game()
    else:
        main()