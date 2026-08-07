from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from chains import llm

summary_prompt = ChatPromptTemplate.from_template(
    """
You are an expert research assistant.

Below are web search results.

Your job is to create a concise research summary.

Rules:
- Keep only the most useful information.
- Remove duplicate information.
- Preserve important facts.
- Preserve URLs if available.
- Maximum 300 words.

Search Results:

{results}
"""
)

summarizer = summary_prompt | llm | StrOutputParser()