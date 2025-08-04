import os
import pandas as pd
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from typing import List, Dict, Any

class MultiFormatRAGSystem:
    def __init__(self, openai_api_key=None):
        """멀티 포맷 RAG 시스템 초기화"""
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # 임베딩 모델 설정 (한국어 지원)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask",
            model_kwargs={'device': 'cpu'}
        )
        
        # 텍스트 분할기 설정
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # LLM 설정
        self.llm = OpenAI(temperature=0)
        
        # 벡터 스토어 초기화
        self.vector_store = None
        self.qa_chain = None

    def load_text_file(self, file_path: str) -> List[Document]:
        """텍스트 파일 로드"""
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            # 메타데이터 추가
            for doc in documents:
                doc.metadata.update({
                    'file_type': 'text',
                    'source': file_path,
                    'filename': os.path.basename(file_path)
                })
            
            return documents
        except Exception as e:
            print(f"텍스트 파일 로드 실패 {file_path}: {e}")
            return []

    def load_pdf_file(self, file_path: str) -> List[Document]:
        """PDF 파일 로드"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # 메타데이터 추가
            for doc in documents:
                doc.metadata.update({
                    'file_type': 'pdf',
                    'source': file_path,
                    'filename': os.path.basename(file_path)
                })
            
            return documents
        except Exception as e:
            print(f"PDF 파일 로드 실패 {file_path}: {e}")
            return []

    def load_excel_file(self, file_path: str) -> List[Document]:
        """엑셀 파일 로드"""
        try:
            documents = []
            
            # 엑셀 파일의 모든 시트 읽기
            xl_file = pd.ExcelFile(file_path)
            
            for sheet_name in xl_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # 데이터가 있는 경우에만 처리
                if not df.empty:
                    # 방법 1: 각 행을 별도 문서로 처리
                    for idx, row in df.iterrows():
                        # NaN 값 제거 후 문자열로 변환
                        row_dict = row.dropna().to_dict()
                        
                        # 행 데이터를 텍스트로 변환
                        content_parts = []
                        for col, value in row_dict.items():
                            content_parts.append(f"{col}: {value}")
                        
                        content = "\n".join(content_parts)
                        
                        doc = Document(
                            page_content=content,
                            metadata={
                                'file_type': 'excel',
                                'source': file_path,
                                'filename': os.path.basename(file_path),
                                'sheet_name': sheet_name,
                                'row_index': idx,
                                'columns': list(row_dict.keys())
                            }
                        )
                        documents.append(doc)
                    
                    # 방법 2: 시트 전체를 하나의 문서로 처리 (추가)
                    sheet_summary = f"시트명: {sheet_name}\n"
                    sheet_summary += f"컬럼: {', '.join(df.columns.tolist())}\n"
                    sheet_summary += f"총 행 수: {len(df)}\n\n"
                    
                    # 처음 5행의 샘플 데이터 포함
                    if len(df) > 0:
                        sheet_summary += "샘플 데이터:\n"
                        for idx, row in df.head().iterrows():
                            row_str = ", ".join([f"{col}: {val}" for col, val in row.dropna().items()])
                            sheet_summary += f"행 {idx}: {row_str}\n"
                    
                    summary_doc = Document(
                        page_content=sheet_summary,
                        metadata={
                            'file_type': 'excel_summary',
                            'source': file_path,
                            'filename': os.path.basename(file_path),
                            'sheet_name': sheet_name,
                            'total_rows': len(df),
                            'columns': df.columns.tolist()
                        }
                    )
                    documents.append(summary_doc)
            
            return documents
            
        except Exception as e:
            print(f"엑셀 파일 로드 실패 {file_path}: {e}")
            return []

    def load_documents(self, file_paths: List[str]) -> List[Document]:
        """다양한 형식의 문서들을 로드"""
        all_documents = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                print(f"파일이 존재하지 않습니다: {file_path}")
                continue
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                docs = self.load_pdf_file(file_path)
            elif file_ext == '.txt':
                docs = self.load_text_file(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                docs = self.load_excel_file(file_path)
            else:
                print(f"지원하지 않는 파일 형식: {file_path}")
                continue
            
            all_documents.extend(docs)
            print(f"로드된 문서: {file_path} ({len(docs)} 청크)")
        
        return all_documents

    def process_documents(self, documents: List[Document]) -> List[Document]:
        """문서 전처리 및 청킹"""
        processed_docs = []
        
        for doc in documents:
            # 엑셀 행 데이터는 이미 적절한 크기이므로 분할하지 않음
            if doc.metadata.get('file_type') == 'excel' and 'row_index' in doc.metadata:
                processed_docs.append(doc)
            else:
                # 텍스트와 PDF는 청킹 수행
                chunks = self.text_splitter.split_documents([doc])
                processed_docs.extend(chunks)
        
        print(f"총 처리된 청크 수: {len(processed_docs)}")
        return processed_docs

    def create_vector_store(self, documents: List[Document], persist_directory="./multi_format_db"):
        """벡터 스토어 생성"""
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=persist_directory
        )
        print("벡터 스토어 생성 완료")

    def load_vector_store(self, persist_directory="./multi_format_db"):
        """기존 벡터 스토어 로드"""
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        print("벡터 스토어 로드 완료")

    def setup_qa_chain(self, chain_type="stuff", k=5):
        """QA 체인 설정"""
        if not self.vector_store:
            raise ValueError("벡터 스토어가 설정되지 않았습니다.")
        
        # 한국어 프롬프트 템플릿
        prompt_template = """다음 컨텍스트를 사용하여 질문에 답하세요.
        컨텍스트에는 텍스트 파일, PDF 파일, 엑셀 파일의 내용이 포함되어 있습니다.
        엑셀 데이터의 경우 구조화된 데이터이므로 정확한 값을 제공하세요.
        답을 찾을 수 없다면 "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답하세요.

        컨텍스트: {context}

        질문: {question}
        답변:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # 검색기 설정
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": k}
        )
        
        # QA 체인 생성
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type=chain_type,
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )

    def query(self, question: str) -> Dict[str, Any]:
        """질문하기"""
        if not self.qa_chain:
            raise ValueError("QA 체인이 설정되지 않았습니다.")
        
        result = self.qa_chain({"query": question})
        
        return {
            "answer": result["result"],
            "source_documents": result["source_documents"]
        }

    def search_by_file_type(self, query: str, file_type: str = None, k: int = 5):
        """파일 타입별 검색"""
        if not self.vector_store:
            raise ValueError("벡터 스토어가 설정되지 않았습니다.")
        
        if file_type:
            # 필터를 사용한 검색
            docs = self.vector_store.similarity_search(
                query, 
                k=k,
                filter={"file_type": file_type}
            )
        else:
            docs = self.vector_store.similarity_search(query, k=k)
        
        return docs

    def get_file_statistics(self):
        """로드된 파일들의 통계 정보"""
        if not self.vector_store:
            return "벡터 스토어가 설정되지 않았습니다."
        
        # 모든 문서 가져오기
        all_docs = self.vector_store.get()
        
        if not all_docs['metadatas']:
            return "문서가 없습니다."
        
        file_types = {}
        filenames = set()
        
        for metadata in all_docs['metadatas']:
            file_type = metadata.get('file_type', 'unknown')
            filename = metadata.get('filename', 'unknown')
            
            if file_type not in file_types:
                file_types[file_type] = 0
            file_types[file_type] += 1
            filenames.add(filename)
        
        stats = f"총 문서 수: {len(all_docs['metadatas'])}\n"
        stats += f"총 파일 수: {len(filenames)}\n"
        stats += "파일 타입별 청크 수:\n"
        for file_type, count in file_types.items():
            stats += f"  - {file_type}: {count}개\n"
        
        return stats

# 사용 예제
def main():
    # 멀티 포맷 RAG 시스템 초기화
    rag = MultiFormatRAGSystem(openai_api_key="your-openai-api-key")
    
    # 다양한 형식의 파일들
    file_paths = [
        "document.txt",      # 텍스트 파일
        "report.pdf",        # PDF 파일
        "data.xlsx",         # 엑셀 파일
        "sales_data.xls",    # 구 버전 엑셀 파일
        # 더 많은 파일들...
    ]
    
    try:
        # 문서 로드 및 처리
        documents = rag.load_documents(file_paths)
        if not documents:
            print("로드된 문서가 없습니다.")
            return
        
        processed_docs = rag.process_documents(documents)
        rag.create_vector_store(processed_docs)
        
        # QA 체인 설정
        rag.setup_qa_chain(k=5)
        
        # 파일 통계 출력
        print("\n=== 파일 통계 ===")
        print(rag.get_file_statistics())
        
        # 질문하기
        print("\n=== 질문 답변 시스템 ===")
        while True:
            question = input("\n질문을 입력하세요 (종료: 'quit'): ")
            if question.lower() == 'quit':
                break
            
            # 일반 질문
            result = rag.query(question)
            print(f"\n답변: {result['answer']}")
            
            # 소스 문서 정보 출력
            print("\n참조 문서:")
            for i, doc in enumerate(result['source_documents']):
                metadata = doc.metadata
                file_type = metadata.get('file_type', 'unknown')
                filename = metadata.get('filename', 'unknown')
                
                print(f"{i+1}. [{file_type}] {filename}")
                
                if file_type == 'excel':
                    sheet = metadata.get('sheet_name', '')
                    row = metadata.get('row_index', '')
                    if sheet and str(row) != '':
                        print(f"   시트: {sheet}, 행: {row}")
                
                print(f"   내용: {doc.page_content[:100]}...")
                print()
        
        # 파일 타입별 검색 예제
        print("\n=== 엑셀 파일만 검색 ===")
        excel_docs = rag.search_by_file_type("매출", "excel", k=3)
        for doc in excel_docs:
            print(f"내용: {doc.page_content[:100]}...")
            print(f"파일: {doc.metadata.get('filename')}")
            print(f"시트: {doc.metadata.get('sheet_name')}")
            print()
                
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()