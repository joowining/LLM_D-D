# rag_system.py

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from transformers import AutoTokenizer, AutoModel
from langchain_core.runnables import chain
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional
#
from prompts.rag_prompt import story_rag_prompt, rule_rag_prompt
from .rag_config import CONFIG


class RAGSystem:
    def __init__(
        self,
        persist_dir: str = CONFIG["persist_dir"],
        embedding_model_id: str = CONFIG["embedding_model_id"],
        device: str = "gpu",
        llm_model: str = CONFIG["llm_model"]
    ):
        """ 벡터 저장소 위치, 임베딩 모델, 임베딩 기기 ( cpu / gpu ), llm모델로 초기 설정 """
        self.persist_dir = persist_dir
        self.embedding_model_id = embedding_model_id
        self.device = device
        self.llm_model = llm_model

        self.embedding = OllamaEmbeddings(
            model= self.embedding_model_id,
            base_url="http://localhost:11434"
        )

        self.vectorstore: Optional[Chroma] = None
        self.retriever = None

        self.prompt: ChatPromptTemplate = None

    def build_vectorstore(self, filepath: str, collection: str):
        """최초 문서 임베딩 및 ChromaDB 저장"""
        # 파일 확장자에 따라 적절한 로더 선택
        if filepath.lower().endswith('.pdf'):
            loader = PyPDFLoader(filepath)
        else:
            loader = TextLoader(filepath, encoding='utf-8')
        
        documents = loader.load()

        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(documents)

        self.vectorstore = Chroma.from_documents(
            docs,
            self.embedding,
            collection_name=collection,
            persist_directory=self.persist_dir
        )
        self.vectorstore.persist()
        print(f"[+] Vector store built and saved to {self.persist_dir}")
 

    def load_vectorstore(self, collection: str):
        """기존 ChromaDB 로드"""
        self.vectorstore = Chroma(
            persist_directory=self.persist_dir,
            collection_name=collection,
            embedding_function=self.embedding
        )
        print(f"[+] Vector store loaded from {self.persist_dir}")

    def query(self, usr_input: str, prompt:str , k:int = 2)-> str:
        '''사용자의 입력, 상황에 맞는 프롬프트 그리고 유사도 k를 입력받아 벡터저장소에서부터 유사문서를 찾아 응답하도록 함 '''
        # 유사 문서 찾기 
        self.retriever = self.vectorstore.as_retriever(search_kwargs = {'k': k})
        docs = self.retriever.invoke(usr_input)
        self.prompt = prompt
        formatted = self.prompt.invoke({'context': docs, 'question': usr_input})
        # 답변생성 
        model = ChatOllama(model= self.llm_model)
        answer = model.invoke(formatted)

        return answer.content


def collection_exists(persist_dir:str, collection_name: str) -> bool:
    try:
        embedding = OllamaEmbeddings(
            model=CONFIG["embedding_model_id"],
            base_url="http://localhost:11434"
        )

        _ = Chroma(
            persist_directory=persist_dir,
            collection_name = collection_name,
            embedding_function=embedding
        )
        print("컬렉션 로드 성공")
        return True
    except Exception as e:
        print("컬렉션 로드 실패 {e}")
        return False

question_type = {
    "rule" : "rulebook",
    "story" : "storybook"
}
prompt_type = {
    "rule" : rule_rag_prompt,
    "story": story_rag_prompt
}

def using_rag(input: str, type: str):
    rag_system = RAGSystem()
    rag_system.load_vectorstore(question_type[type])
    answer = rag_system.query(input, prompt_type[type] )
    return answer


if __name__ == "__main__":
    persist_dir = "./chroma_db_exaone"
    rule_collection_name = "rulebook"
    story_collection_name = "storybook"

    rule_rag = RAGSystem()
    story_rag = RAGSystem()

    import os
    
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print("벡터 저장소 존재")
        if collection_exists(persist_dir, rule_collection_name):
            rule_rag.load_vectorstore(rule_collection_name)
            rule_input = input("input your question about rule \n > ")
            answer = rule_rag.query(rule_input, rule_rag_prompt)
            print(f"룰 응답 : {answer}") 
        else:
            print("룰 컬렉션이 없음 생성 필요")

        if collection_exists(persist_dir, story_collection_name):
            story_rag.load_vectorstore(story_collection_name)
            story_input = input("input your question about story \n > ")
            answer = story_rag.query(story_input, story_rag_prompt)
            print(f"스토리 응답 : {answer}")
        else:
            print("스토리 컬렉션이 없음 생성 필요")
    else: 
        rule_rag.build_vectorstore(CONFIG["rule_file"], rule_collection_name)
        story_rag.build_vectorstore(CONFIG["story_file"], story_collection_name)
        print("생성 완료")





