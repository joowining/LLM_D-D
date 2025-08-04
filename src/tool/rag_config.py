# rag_config.py
''' 
rag system 에 대한 configuration data
'''

CONFIG = {
    "persist_dir": "./chroma_db_exaone",
    #"embedding_model_id": "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct",
    "embedding_model_id":"bona/bge-m3-korean",
    #"llm_model": "exaone3.5:latest",
    "llm_model":"benedict/linkbricks-llama3.1-korean:8b",
    "rule_file": "./document_data/DND_Rulebook.pdf",
    "story_file": "./document_data/background_story.txt"
}