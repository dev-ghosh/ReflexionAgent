from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from chains import revisor, first_responder
from tool_executor import execute_tools_node
from summarizer import summarizer
from state import GraphState

MAX_ITERATIONS = 2


def draft_node(state: GraphState):
    response = first_responder.invoke({"messages": state["messages"]})
    return {"messages": [response]}


def revise_node(state: GraphState):
    response = revisor.invoke(
        {
            "messages": state["messages"],
            "search_summary": state["search_summary"],
        }
    )
    return {"messages": [response], "iteration": state["iteration"] + 1}


def summarize_node(state: GraphState):
    summary = summarizer.invoke({"results": state["search_results"]})
    return {"search_summary": summary}


def event_loop(state: GraphState) -> Literal["execute_tools", END]:
    if state["iteration"] >= MAX_ITERATIONS:
        return END
    return "execute_tools"


def build_graph():
    builder = StateGraph(GraphState)
    builder.add_node("draft", draft_node)
    builder.add_node("execute_tools", execute_tools_node)
    builder.add_node("revise", revise_node)
    builder.add_node("summarize", summarize_node)
    builder.add_edge(START, "draft")
    builder.add_edge("draft", "execute_tools")
    builder.add_edge("execute_tools", "summarize")
    builder.add_edge("summarize", "revise")
    builder.add_conditional_edges("revise", event_loop, ["execute_tools", END])
    return builder.compile()


def run_agent(question: str):
    """Run the reflexion graph for a question and return the raw final state."""
    graph = build_graph()
    return graph.invoke(
        {
            "messages": [{"role": "user", "content": question}],
            "search_results": "",
            "search_summary": "",
            "iteration": 0,
        }
    )


def extract_result(res: dict):
    """
    Pulls out: final answer, references, and per-step reflexion critiques
    (missing/superfluous) from every draft/revision so the UI can show
    both the clean answer and the critique history separately.
    """
    critiques = []
    final_answer, references = "", []

    ai_messages = [m for m in res["messages"] if isinstance(m, AIMessage) and m.tool_calls]

    for i, msg in enumerate(ai_messages):
        args = msg.tool_calls[0]["args"]
        label = "Initial Draft" if i == 0 else f"Revision {i}"
        reflection = args.get("reflection", {})
        critiques.append(
            {
                "label": label,
                "missing": reflection.get("missing", ""),
                "superfluous": reflection.get("superfluous", ""),
            }
        )

    if ai_messages:
        last_args = ai_messages[-1].tool_calls[0]["args"]
        final_answer = last_args.get("answer", "")
        references = last_args.get("references", [])

    return final_answer, references, critiques


if __name__ == "__main__":
    result = run_agent("What is Python?")
    answer, refs, critiques = extract_result(result)
    print(answer)
    print(refs)
    print(critiques)