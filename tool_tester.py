from dotenv import load_dotenv
load_dotenv(".env.rex", override=True)

from langchain_groq import ChatGroq
from schemas import AnswerQuestion
from langchain_core.messages import HumanMessage

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
)

llm = llm.bind_tools(
    tools=[AnswerQuestion],
    tool_choice="AnswerQuestion",
)

response = llm.invoke(
    [
        HumanMessage(
            content="What is Python?"
        )
    ]
)

print(response)