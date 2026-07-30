import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from pydantic import BaseModel

from graph.workflow import build_graph
from rag.reranker import get_reranker
import pandas as pd
from fastapi import HTTPException
from fastapi.responses import FileResponse

from utils.results_logger import log_result, LOG_PATH

app = FastAPI(title="CiteGuard API", description="Documentation Q&A with citation verification")

get_reranker()  # wymusza załadowanie modelu przy starcie, nie przy pierwszym request
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

    log_result(
        question=request.question,
        answer=result["answer"],
        verified=result["verified"],
        reasoning=result["reasoning"],
    )

    return AnswerResponse(
        answer=result["answer"],
        verified=result["verified"],
        reasoning=result["reasoning"]
    )


@app.get("/export/csv")
def export_csv():
    if not os.path.isfile(LOG_PATH):
        raise HTTPException(status_code=404, detail="Brak zapisanych wynikow - najpierw zadaj przynajmniej jedno pytanie")
    return FileResponse(LOG_PATH, filename="citeguard_results.csv", media_type="text/csv")


@app.get("/export/excel")
def export_excel():
    if not os.path.isfile(LOG_PATH):
        raise HTTPException(status_code=404, detail="Brak zapisanych wynikow - najpierw zadaj przynajmniej jedno pytanie")

    df = pd.read_csv(LOG_PATH)
    excel_path = "./data/citeguard_results.xlsx"
    df.to_excel(excel_path, index=False)

    return FileResponse(
        excel_path,
        filename="citeguard_results.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )