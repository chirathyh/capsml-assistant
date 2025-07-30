from typing import TypedDict

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from agents import CodeAgent, AssistantAgent

# ——————————————————————————————————————
# State Schema
# ——————————————————————————————————————
class GraphState(TypedDict):
    input: str
    code_agent: str
    assistant_agent: str
    refined_query: str
    use_pdf: bool
    use_web: bool
    use_code: bool
    pdf_results: str
    web_results: str
    code_results: str
    summary_pdf: str
    summary_web: str
    summary_code: str
    report: str


def build_graph():

    # setup agents
    code_agent = CodeAgent()
    assistant_agent = AssistantAgent()

    # setup graph
    builder = StateGraph(GraphState)

    builder.add_node("analyze_query", RunnableLambda(assistant_agent.analyze_query))

    builder.add_node("retrieve_pdf", RunnableLambda(assistant_agent.retrieve_pdf))
    builder.add_node("retrieve_web", RunnableLambda(assistant_agent.retrieve_web))
    builder.add_node("retrieve_code", RunnableLambda(code_agent.retrieve))

    builder.add_node("summarize_pdf", RunnableLambda(assistant_agent.summarize_pdf))
    builder.add_node("summarize_web", RunnableLambda(assistant_agent.summarize_web))
    builder.add_node("summarize_code", RunnableLambda(code_agent.summarize))

    builder.add_node("integrate", RunnableLambda(assistant_agent.integrate))

    builder.set_entry_point("analyze_query")

    builder.add_edge("analyze_query", "retrieve_pdf")
    builder.add_edge("analyze_query", "retrieve_web")
    builder.add_edge("analyze_query", "retrieve_code")

    builder.add_edge("retrieve_pdf", "summarize_pdf")
    builder.add_edge("retrieve_web", "summarize_web")
    builder.add_edge("retrieve_code", "summarize_code")

    builder.add_edge("summarize_pdf", "integrate")
    builder.add_edge("summarize_web", "integrate")
    builder.add_edge("summarize_code", "integrate")

    builder.add_edge("integrate", END)

    return builder.compile()
