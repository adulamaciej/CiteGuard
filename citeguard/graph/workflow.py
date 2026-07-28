from typing import TypedDict
from langgraph.graph import StateGraph, END

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.retriever import retrieve_relevant_chunks
from agents.answer_agent import generate_answer
from agents.citation_checker_agent import check_citations


class CiteGuardState(TypedDict):
    question: str
    chunks: list
    answer: str
    verified: bool
    reasoning: str


def retrieve_node(state: CiteGuardState) -> CiteGuardState:
    chunks = retrieve_relevant_chunks(state["question"])
    return {**state, "chunks": chunks}


def answer_node(state: CiteGuardState) -> CiteGuardState:
    answer = generate_answer(state["question"], state["chunks"])
    return {**state, "answer": answer}


def verify_node(state: CiteGuardState) -> CiteGuardState:
    check = check_citations(state["question"], state["answer"], state["chunks"])
    return {**state, "verified": check["verified"], "reasoning": check["reasoning"]}


def build_graph():
    graph = StateGraph(CiteGuardState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("answer", answer_node)
    graph.add_node("verify", verify_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", "verify")
    graph.add_edge("verify", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"question": "How do I build a multi-agent system with LangGraph?"})

    print(f"=== ANSWER ===\n{result['answer']}\n")
    print(f"=== VERIFIED ===\n{result['verified']}\n")
    print(f"=== REASONING ===\n{result['reasoning']}")