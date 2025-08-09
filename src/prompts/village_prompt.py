from langchain_core.prompts import ChatPromptTemplate

# prompt 1. param : Basic Village Script
village_intro_prompt = ChatPromptTemplate.from_template("""

""")

# prompt 2. param : user_input, system_message 
village_user_input_analysis_prompt = ChatPromptTemplate.from_template("""

""")

# prompt 3. param : user_input, context, villaga_rag_data
village_look_around_RAG_prompt = ChatPromptTemplate.from_template("""


""")

# prompt 4. param : village_rag_data
village_npc_choice_prompt = ChatPromptTemplate.from_template("""


""")

# prompt 5. param : village_rag_data, user_input
village_npc_choice_analysis_prompt = ChatPromptTemplate.from_template("""


""")

# prompt 6. param : npc name, village_rag_data
village_npc_persona_prompt = ChatPromptTemplate.from_template("""

""")


# prompt 7. param : user_input, village_summary
village_other_question_prompt = ChatPromptTemplate.from_template("""

""")

