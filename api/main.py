import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from pydantic import BaseModel

from graph.workflow import build_graph

app = FastAPI(title="CiteGuard API", description="Documentation Q&A with citation verification")

graph_app = build_graph()


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    verified: bool
    reasoning: str


@app.get("/")
def root():
    return {"status": "CiteGuard API is running"}


@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    result = graph_app.invoke({"question": request.question})
    return AnswerResponse(
        answer=result["answer"],
        verified=result["verified"],
        reasoning=result["reasoning"]
    )