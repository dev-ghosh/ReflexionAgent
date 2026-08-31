import datetime
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env.rex"), override=True)
#load_dotenv(".env.rex",override=True)

from langchain_core.messages import HumanMessage
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

from schemas import AnswerQuestion, ReviseAnswer

llm = ChatGroq(
    temperature=0,
    model="openai/gpt-oss-20b"
)
parser = JsonOutputToolsParser(return_id=True)
parser_pydantic = PydanticToolsParser(tools=[AnswerQuestion])

actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert researcher.

Current time: {time}

Your job is to answer the user's question.

Instructions:
1. {first_instruction}
3. Use the following summarized web search results while improving your answer.
   Search Summary:
   {search_summary}
3. Critically evaluate your own answer.
4. Identify what important information is missing.
5. Identify any unnecessary information.
6. Generate 1-2 search queries that would help improve the answer.
7. You MUST respond by calling the appropriate tool.
Do NOT answer in plain text.
""",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
).partial(
    time=lambda: datetime.datetime.now().isoformat(),
    search_summary=""
)


first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="""
    Provide a detailed answer of approximately 250 words.

    You MUST respond by calling the AnswerQuestion tool.
    Do not answer in plain text.
    """
)

first_responder = first_responder_prompt_template | llm.bind_tools(
    tools=[AnswerQuestion], tool_choice="AnswerQuestion"
)

revise_instructions = """Revise your previous answer using the new information.
    - You should use the previous critique to add important information to your answer.
        - You MUST include numerical citations in your revised answer to ensure it can be verified.
        - Add a "References" section to the bottom of your answer (which does not count towards the word limit). In form of:
            - [1] https://example.com
            - [2] https://example.com
    - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more than 250 words.
"""

revisor = actor_prompt_template.partial(
    first_instruction=revise_instructions
) | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer")


# if __name__ == "__main__":
#     human_message = HumanMessage(
#         content="Write about AI-Powered SOC / autonomous soc  problem domain,"
#         " list startups that do that and raised capital."
#     )
#     chain = (
#         first_responder_prompt_template
#         | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
#         | parser_pydantic
#     )
#
#     res = chain.invoke(input={"messages": [human_message]})
#     print(res)
