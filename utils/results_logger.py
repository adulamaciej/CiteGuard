import csv
import os
from datetime import datetime
from config import BASE_DIR


LOG_PATH = os.path.join(BASE_DIR, "data", "results_log.csv")


FIELDNAMES = ["timestamp", "question", "answer", "verified", "reasoning"]


def log_result(question: str, answer: str, verified: bool, reasoning: str):

    """Appends one row to a CSV after each /ask call."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)

    with open(LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.utcnow().isoformat(),
            "question": question,
            "answer": answer,
            "verified": verified,
            "reasoning": reasoning,
        })