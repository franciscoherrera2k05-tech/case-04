import json
from pathlib import Path
from datetime import datetime
from typing import Mapping, Any

RESULTS_PATH = Path("data/survey.ndjson")

def append_json_line(record: Mapping[str, Any]) -> None:
    # Ensure the folder exists
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Convert None values to empty strings for optional fields
    clean_record = {k: (v if v is not None else "") for k, v in record.items()}
    with RESULTS_PATH.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps(
                clean_record,
                ensure_ascii=False,
                default=lambda o: o.isoformat() if isinstance(o, datetime) else o
            ) + "\n"
        )
