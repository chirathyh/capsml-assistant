from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

from tools import web_search, clone_and_markdown, load_and_embed_pdfs


# Memory store
MEMORY_LOG: List[str] = []

class CodeAgent:
    def __init__(self, default_repo_url=None):
        self.name = "CodeAgent"
        self.llm = None
        self.repo_url = default_repo_url or "https://github.com/RL4H/RL4T1D.git"
        self.task = "Summarize and explain the following GitHub repo contents providing code snippets:"

    def summarize(self, state):
        
        self.llm = ChatOllama(model=state["code_agent"])
        
        code_content = state.get("code_results", "")
        if not code_content:
            return {"summary_code": ""}
        
        summary = self.llm.invoke([
            HumanMessage(content=f"{self.task}\n\n{code_content}")
        ]).content

        return {"summary_code": summary}
    
    def retrieve(self, state):
        if not state.get("use_code", False):
            return {"code_results": ""}
        refined_query = state["refined_query"]
        hits = clone_and_markdown(self.repo_url)  # TODO: Here, you can enhance logic to dynamically determine repo URL based on query
        return {"code_results": hits}

    

class AssistantAgent:
    def __init__(self):
        self.name = "AssistantAgent"
        self.llm = None

    def analyze_query(self, state):
        
        self.llm = ChatOllama(model=state["assistant_agent"])
        
        query = state["input"]
        refined = self.llm.invoke([HumanMessage(content=f"You are the Query Analyzer. Refine and expand the user’s query into a single, improved query string.: '{query}'")]).content
        return {"refined_query": refined}

    def retrieve_pdf(self, state):
        if not state.get("use_pdf", False):
            return {"pdf_results": ""}
        refined = state["refined_query"]
        hits = load_and_embed_pdfs(refined)
        return {"pdf_results": hits}


    def summarize_pdf(self, state):
        text = state["pdf_results"]
        summary = self.llm.invoke([HumanMessage(content=f"Summarize the following PDF content:\n\n{text}")]).content
        return {"summary_pdf": summary}


    def retrieve_web(self, state):
        if not state.get("use_web", False):
            return {"web_results": ""}
        refined = state["refined_query"]
        hits = web_search(refined)
        return {"web_results": hits}

    def summarize_web(self, state):
        text = state["web_results"]
        summary = self.llm.invoke([HumanMessage(content=f"Summarize the following web snippets:\n\n{text}")]).content
        return {"summary_web": summary}

    def integrate(self, state):
        pdf = state["summary_pdf"]
        web = state["summary_web"]
        code = state["summary_code"]
        report = self.llm.invoke([HumanMessage(content=f"You are the Integrator. Merge summaries (some may be empty), highlight contradictions or gaps, and produce a final polished report..\n\n=== PDF ===\n{pdf}\n\n=== WEB ===\n{web}\n\n=== CODE ===\n{code}")]).content
        MEMORY_LOG.append(f"Q: {state['input']}\n\nA:\n{report}\n")
        return {"report": report}


# if __name__ == "__main__":
#     question = "Explain how the G2P2C system works for glucose regulation?"
#     result = graph.invoke({
#         "input": question,
#         "use_pdf": False,
#         "use_web": False,
#         "use_code": False
#     })
#     print("\n===== FINAL REPORT =====\n")
#     print(result["report"])
