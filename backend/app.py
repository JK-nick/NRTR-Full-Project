"""Simple Flask backend powering NRTR resources APIs."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

from dotenv import load_dotenv
from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

POST /api/login

# Load optional environment overrides from backend/.env
load_dotenv(BASE_DIR / ".env")

RESOURCES: List[Dict[str, Any]] = []
OPPORTUNITIES: List[Dict[str, Any]] = []

def load_dataset(filename: str) -> List[Dict[str, Any]]:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")
    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)

def bootstrap_data() -> None:
    global RESOURCES, OPPORTUNITIES
    RESOURCES = load_dataset("resources.json")
    OPPORTUNITIES = load_dataset("scholarships.json")

def normalize(value: Any) -> Any:
    return value.lower() if isinstance(value, str) else value

def apply_filters(
    items: Iterable[Dict[str, Any]],
    *,
    exact_filters: Dict[str, str],
    search_query: str | None = None,
    search_fields: Iterable[str] = (),
) -> List[Dict[str, Any]]:
    cleaned_filters = {k: v for k, v in exact_filters.items() if v}
    q = search_query.lower() if search_query else None

    def matches(item: Dict[str, Any]) -> bool:
        for field, expected in cleaned_filters.items():
            value = item.get(field)
            if value is None or normalize(value) != normalize(expected):
                return False
        if q:
            haystack = " ".join(str(item.get(field, "")) for field in search_fields)
            if q not in haystack.lower():
                return False
        return True

    return [item for item in items if matches(item)]

def create_app() -> Flask:
    bootstrap_data()

    app = Flask(__name__)

    @app.get("/api/health")
    def health() -> Any:
        return jsonify({"status": "ok", "resources": len(RESOURCES), "opportunities": len(OPPORTUNITIES)})

    @app.get("/api/resources")
    def list_resources() -> Any:
        county = request.args.get("county")
        resource_type = request.args.get("type")
        query = request.args.get("q")
        limit = request.args.get("limit", type=int)

        filtered = apply_filters(
            RESOURCES,
            exact_filters={"county": county, "type": resource_type},
            search_query=query,
            search_fields=["name", "description", "county", "type"],
        )

        if limit:
            filtered = filtered[: max(limit, 0)]

        return jsonify({"count": len(filtered), "results": filtered})

    @app.get("/api/resources/<resource_id>")
    def get_resource(resource_id: str) -> Any:
        matches = [r for r in RESOURCES if r.get("id") == resource_id]
        if not matches:
            return jsonify({"error": "Resource not found"}), 404
        return jsonify(matches[0])

    @app.get("/api/opportunities")
    def list_opportunities() -> Any:
        county = request.args.get("county")
        category = request.args.get("category")
        query = request.args.get("q")
        limit = request.args.get("limit", type=int)

        filtered = apply_filters(
            OPPORTUNITIES,
            exact_filters={"county": county, "category": category},
            search_query=query,
            search_fields=["title", "description", "county", "category"],
        )

        if limit:
            filtered = filtered[: max(limit, 0)]

        return jsonify({"count": len(filtered), "results": filtered})

    @app.get("/api/opportunities/<opportunity_id>")
    def get_opportunity(opportunity_id: str) -> Any:
        matches = [o for o in OPPORTUNITIES if o.get("id") == opportunity_id]
        if not matches:
            return jsonify({"error": "Opportunity not found"}), 404
        return jsonify(matches[0])

    @app.get("/api/meta/counties")
    def list_counties() -> Any:
        counties = sorted({r.get("county") for r in RESOURCES if r.get("county")})
        return jsonify({"counties": counties})

    @app.get("/api/meta/stats")
    def stats() -> Any:
        def tally(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
            counts: Dict[str, int] = {}
            for item in items:
                k = item.get(key)
                if not k:
                    continue
                counts[k] = counts.get(k, 0) + 1
            return counts

        return jsonify(
            {
                "resources_by_county": tally(RESOURCES, "county"),
                "resources_by_type": tally(RESOURCES, "type"),
                "opportunities_by_county": tally(OPPORTUNITIES, "county"),
                "opportunities_by_category": tally(OPPORTUNITIES, "category"),
            }
        )
    
    from flask import Flask, jsonify, request
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)  # allow frontend to access backend locally

    # Demo login user
    USERS = {
        "demo@nrtr.org": "demo123",
        "admin@nrtr.org": "adminpass"
    }

    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if email in USERS and USERS[email] == password:
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401

    if __name__ == "__main__":
        app.run(debug=True)


    return app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") not in {"0", "false", "False"}
    app.run(host=host, port=port, debug=debug)
