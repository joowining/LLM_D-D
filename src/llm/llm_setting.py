from langchain_ollama import ChatOllama, OllamaLLM, OllamaEmbeddings

from dotenv import load_dotenv
import os

load_dotenv()

ChatModel = ChatOllama(model=f"{os.getenv('LLM_MODEL_NAME')}")
LLM = OllamaLLM(model=f"{os.getenv('LLM_MODEL_NAME')}")
LLM_Embedings = OllamaEmbeddings(model=f"{os.getenv('LLM_MODEL_NAME')}")