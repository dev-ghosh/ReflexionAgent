from typing import Literal

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import END, START, StateGraph

from chains import revisor, first_responder
from tool_executor import execute_tools_node

#changes
from summarizer import summarizer

#changes2
from state import GraphState

MAX_ITERATIONS = 2


def draft_node(state: GraphState):
    """Draft the initial response."""
    response = first_responder.invoke({"messages": state["messages"]})
    return {"messages": [response]}


def revise_node(state: GraphState):
    """Revise the answer based on tool results."""
    # response = revisor.invoke({"messages": state["messages"]})
    response = revisor.invoke(
        {
            "messages": state["messages"],
            "search_summary": state["search_summary"],
        }
    )
    return {
        "messages": [response],
        "iteration": state["iteration"] + 1
    }

#changes
def summarize_node(state: GraphState):

    summary = summarizer.invoke(
        {
            "results": state["search_results"]
        }
    )

    return {
        "search_summary": summary
    }


def event_loop(state: GraphState) -> Literal["execute_tools", END]:
    """Determine whether to continue or end based on iteration count."""
    # count_tool_visits = sum(
    #     isinstance(item, ToolMessage) for item in state["messages"]
    # )
    # num_iterations = count_tool_visits
    # if num_iterations > MAX_ITERATIONS:
    #     return END
    # return "execute_tools"
    iteration = state["iteration"]

    if iteration >= MAX_ITERATIONS:
        return END

    return "execute_tools"


builder = StateGraph(GraphState)
builder.add_node("draft", draft_node)
builder.add_node("execute_tools", execute_tools_node)
builder.add_node("revise", revise_node)
builder.add_node("summarize", summarize_node)
builder.add_edge(START, "draft")
builder.add_edge("draft", "execute_tools")
# builder.add_edge("execute_tools", "revise")
#changes
builder.add_edge("execute_tools", "summarize")
builder.add_edge("summarize", "revise")
builder.add_conditional_edges("revise", event_loop, ["execute_tools", END])
graph = builder.compile()

#print(graph.get_graph().draw_mermaid())
graph.get_graph().draw_mermaid_png(output_file_path="flow.png")




res = graph.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is Python?"
            }
        ],
        "search_results": "",
        "search_summary": "",
        "iteration": 0,
    }
)
# Extract the final answer from the last message with tool calls
last_message = res["messages"][-1]

if isinstance(last_message, AIMessage):

    if last_message.tool_calls:
        print(last_message.tool_calls[0]["args"]["answer"])

    else:
        print(last_message.content)

print(res)


