from langchain_ollama import ChatOllama, OllamaLLM, OllamaEmbeddings

from dotenv import load_dotenv

load_dotenv()

ChatModel = ChatOllama(model='LLM_MODEL_NAME')
LLM = OllamaLLM(model='LLM_MODEL_NAME')
LLM_Embedings = OllamaEmbeddings(model='LLM_MODEL_NAME')