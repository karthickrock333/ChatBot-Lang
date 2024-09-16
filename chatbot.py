# from langchain.llms import GooglePalm
import os

from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

from langchain.prompts import SemanticSimilarityExampleSelector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import FewShotPromptTemplate
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX, _mysql_prompt
from langchain.prompts.prompt import PromptTemplate
from langchain_community.llms import OpenAI
# from few_shots import few_shots
# # import os
#
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env (especially openai api key)
few_shots = [
    {'Question': "Can you provide the first and last names of all providers who are listed as Orthopedic specialists?",
     'SQLQuery': "SELECT PROVIDERFIRSTNAME, PROVIDERLASTNAME FROM provider WHERE SPECIALTY = 'Orthopedic' limit 1;",
     'SQLResult': "Result of the SQL query",
     'Answer': "0"},

    {'Question': "What is the provider type for the provider named 'Makayla Ellis'?",
     'SQLQuery': "SELECT PROVIDERTYPE FROM provider WHERE PROVIDERFIRSTNAME = 'Makayla' AND PROVIDERLASTNAME = 'Ellis';",
     'SQLResult': "Result of the SQL query",
     'Answer': "DO"},

    {
        'Question': "Could you provide me with the patient IDs for all clinical encounters where the encounter type is 'CL'?",
        'SQLQuery': "select PATIENTID FROM CILINCALENCOUNTER WHERE CLINICALENCOUNTERTYPE='CL'",
        'SQLResult': "Result of the SQL query",
        'Answer': " "},

    {
        'Question': "Can you provide the patient IDs for clinical encounters where the encounter type is 'CL' and the parent context ID is 2001?",
        'SQLQuery': "select PATIENTID FROM CILINCALENCOUNTER WHERE CLINICALENCOUNTERTYPE='CL' AND CONTEXTPARENTCONTEXTID = 2001",
        'SQLResult': "Result of the SQL query",
        'Answer': " "},

    {'Question': "What is the patient's email address and their primary provider's last name?",
     'SQLQuery': "SELECT p.EMAIL, prv.PROVIDERLASTNAME FROM patient p JOIN provider prv ON p.PRIMARYPROVIDERID = prv.PROVIDERID limit 1;",
     'SQLResult': "Result of the SQL query",
     'Answer': " "},

    {'Question': "give me patient details of this patientid 361",
     'SQLQuery': "SELECT PROVIDERFIRSTNAME, PROVIDERLASTNAME FROM provider WHERE SPECIALTY = 'Orthopedic' limit 1;",
     'SQLResult': "Result of the SQL query",
     'Answer': "0"},

    # {'Question': "Number of unique sales orders",
    #  'SQLQuery': ''' SELECT COUNT(DISTINCT m_soid) AS num_sales_orders FROM sales;''',
    #  'SQLResult': "Result of the SQL query",
    #  'Answer': "14"},
    # {'Question': "Number of units fulfilled for the Boot Barn Dorag Cap Skull ",
    #  'SQLQuery': "SELECT SUM(m_qtyfulfilled) AS total_qty_fulfilled FROM sales WHERE m_soitem_desc = 'Boot Barn Dorag Cap Skull';",
    #  'SQLResult': "Result of the SQL query",
    #  'Answer': "8"},
    # {'Question': "Number of units fulfilled for the Boot Barn Dorag Cap Skull ",
    #  'SQLQuery': "SELECT SUM(m_qtyfulfilled) AS total_qty_fulfilled FROM sales WHERE m_soitem_desc = 'Boot Barn Dorag Cap Skull';",
    #  'SQLResult': "Result of the SQL query",
    #  'Answer': "8"}
]


def get_few_shot_db_chain():
    db = SQLDatabase.from_uri(
        "snowflake://Jeyasudha:Sep12345@mm75865.ap-south-1/HC_INSIGHTS/PUBLIC?role=ACCOUNTADMIN&warehouse=COMPUTE_WH",
        sample_rows_in_table_info=3)

    #     api_key = 'AIzaSyBtyMTpmbQXkDB41VXAMLKy_YgBrIiE10w'
    #     llm = GooglePalm(google_api_key=api_key, temperature=0.1)

    os.environ['OPENAI_API_KEY'] = 'API_KEY_HERE'
    llm = OpenAI(temperature=0.1, max_tokens=500, model_name='gpt-4')

    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    to_vectorize = [" ".join(example.values()) for example in few_shots]
    vectorstore = Chroma.from_texts(to_vectorize, embeddings, metadatas=few_shots)
    example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vectorstore,
        k=1,
    )
    mysql_prompt = """SS Chatbot SQL Server Expert

    Your name is SS Chatbot, a SQL Server expert. Respond to each question by first crafting a syntactically correct SQL Server query and then providing an answer based on the query results.

    Rules:

    1. Query Structure:
       - Always use proper snowflake  syntax.
       - Use the `TOP` clause to retrieve a maximum of {top_k} results unless specified otherwise.
       - Use `CURRENT_DATE` for queries involving today's date.
       - Wrap each column name in double quotes ("") to denote them as delimited identifiers.
       - Do not use numerical values at the start of SQL variables.
       - Never query all columns; select only the necessary ones to answer the question.
       - refer SME table for each column name  
       -use column name as capital while generating query  

    2. Results Presentation:
       - Provide answers in complete sentences or tables, as appropriate.
       - Format the results in a table if the question asks for a list or details of multiple items.
       - If the user requests a chart format, respond with a dictionary where keys are column names and values are lists of column values.

    3. Language and Character:
       - Respond in the language used in the question.
       - Always stay in character as SS Chatbot.

    4. Error Handling:
       - Validate column names and table relationships to avoid querying non-existent data.
       - If the information is not available or the question is unclear, ask for clarification or state the limitation.

    5. Relevance Filtering:

        - If a question is irrelevant, unrelated to the database content, or outside the scope of SS Chatbot's expertise,
          respond by informing the user that the question is not applicable or does not pertain to the available data.
        - If SQLQuery is N/A, the SS chatbot should respond that the question is irrelevant.


    Response Format:

    -Question: [User's question]
    -SQLQuery: [Constructed SQL query]
    -SQLResult: [Summary of the result or data in dictionary format]
    -Answer: [Final answer]

    No pre-amble. """

    example_prompt = PromptTemplate(
        input_variables=["Question", "SQLQuery", "SQLResult", "Answer"],
        template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",

    )

    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=mysql_prompt,
        suffix=PROMPT_SUFFIX,
        input_variables=["input", "table_info", "top_k"],  # These variables are used in the prefix and suffix
    )
    chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, prompt=few_shot_prompt)
    print(example_prompt)
    return chain


if __name__ == "__main__":
    chain = get_few_shot_db_chain()
    print(chain.run(''' How many homeless people's are is single '''))