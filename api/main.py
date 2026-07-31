import os
import sys
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic import BaseModel
from config import BASE_DIR
from graph.workflow import build_graph
from rag.reranker import get_reranker
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from utils.results_logger import log_result, fetch_all_results, fetch_stats
from dotenv import load_dotenv

load_dotenv()

from logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(title="CiteGuard API", description="Documentation Q&A with citation verification")


get_reranker() 
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
    logger.info(f"Received question: {request.question}")

    try:
        result = graph_app.invoke({"question": request.question})
    except Exception as e:
        logger.error(f"Pipeline failed for question '{request.question}': {e}")
        raise HTTPException(
            status_code=502,
            detail="The AI service is temporarily unavailable. Please try again in a moment."
        )
    
    logger.info(f"Answer verified: {result['verified']}")

    try:
        log_result(
        question=request.question,
        answer=result["answer"],
        verified=result["verified"],
        reasoning=result["reasoning"],
    )
    except Exception as e:
        logger.error(f"Failed to log result: {e}")
    # don't fail the request just because logging failed

    return AnswerResponse(
        answer=result["answer"],
        verified=result["verified"],
        reasoning=result["reasoning"]
    )

@app.get("/stats")
def stats():
    results = fetch_stats()
    if not results:
        raise HTTPException(status_code=404, detail="No results saved yet - ask at least one question first")
    return {"stats": results}


@app.get("/export/csv")
def export_csv():
    results = fetch_all_results()
    if not results:
        raise HTTPException(status_code=404, detail="No results saved yet - ask at least one question first")

    df = pd.DataFrame(results)
    csv_path = os.path.join(BASE_DIR, "data", "citeguard_results.csv")
    df.to_csv(csv_path, index=False)

    return FileResponse(csv_path, filename="citeguard_results.csv", media_type="text/csv")


@app.get("/export/excel")
def export_excel():
    results = fetch_all_results()
    if not results:
        raise HTTPException(status_code=404, detail="No results saved yet - ask at least one question first")

    df = pd.DataFrame(results)
    excel_path = os.path.join(BASE_DIR, "data", "citeguard_results.xlsx")
    df.to_excel(excel_path, index=False)

    return FileResponse(
        excel_path,
        filename="citeguard_results.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )