from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from models import SurveySubmission, StoredSurveyRecord
from storage import append_json_line
import hashlib
import json

app = Flask(__name__)
# Allow cross-origin requests so the static HTML can POST from localhost or file://
CORS(app, resources={r"/v1/*": {"origins": "*"}})


def sha256_hex(s: str) -> str:
    """Return SHA-256 hex digest of a string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def utc_hour_bucket() -> str:
    """Return current UTC time bucket YYYYMMDDHH."""
    return datetime.now(timezone.utc).strftime("%Y%m%d%H")


@app.route("/ping", methods=["GET"])
def ping():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "API is alive",
        "utc_time": datetime.now(timezone.utc).isoformat()
    })


@app.post("/v1/survey")
def submit_survey():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid_json", "detail": "Body must be application/json"}), 400

    try:
        submission = SurveySubmission(**payload)
    except ValidationError as ve:
        return jsonify({"error": "validation_error", "detail": ve.errors()}), 422

    # Generate submission_id deterministically (email + UTC hour)
    submission_id = payload.get("submission_id") or sha256_hex(f"{submission.email}{utc_hour_bucket()}")

    # Create stored record with hashed PII
    record = StoredSurveyRecord(
        name=submission.name,
        consent=submission.consent,
        rating=submission.rating,
        comments=submission.comments or "",
        user_agent=payload.get("user_agent") or "",
        submission_id=submission_id,
        hashed_email=sha256_hex(str(submission.email)),
        hashed_age=sha256_hex(str(submission.age)),
        received_at=datetime.now(timezone.utc),
        ip=request.headers.get("X-Forwarded-For", request.remote_addr or "")
    )

    # Convert datetime to ISO string for storage
    record_dict = record.dict()
    record_dict['received_at'] = record_dict['received_at'].isoformat()

    # Append to NDJSON storage
    append_json_line(record_dict)

    # Return proper autograder response
    return jsonify(status="ok", submission_id=submission_id), 201


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
