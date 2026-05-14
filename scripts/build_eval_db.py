"""Load classified.jsonl into database/eval.sqlite for evaluation."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "eval.sqlite"
PROCESSED = ROOT / "data" / "processed" / "classified.jsonl"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS samples (
            id TEXT PRIMARY KEY,
            source TEXT,
            text TEXT,
            predicted_label TEXT,
            raw_scores TEXT
        )
        """
    )
    conn.commit()
    # TODO: read PROCESSED JSONL and INSERT.
    print(f"Stub: schema ready at {DB_PATH}; ingest from {PROCESSED}")
    conn.close()


if __name__ == "__main__":
    main()
