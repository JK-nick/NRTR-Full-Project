# NRTR Backend

Lightweight Flask backend that exposes read-only APIs for NRTR resources, opportunities, and quick stats. The frontend remains untouched—this service simply reads structured JSON data and makes it available via HTTP.

## Features
- `/api/resources` – filter by county, type, or search text
- `/api/opportunities` – filter by county, category (scholarship/job/internship), or search text
- `/api/meta/*` – fetch county lists and aggregate stats for visualizations
- `/api/health` – simple readiness probe for deployments

## Getting Started

1. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **(Optional) Configure environment**
   - Copy `.env.example` to `.env` and adjust `FLASK_PORT`, `FLASK_DEBUG`, etc.
4. **Run the server**
   ```bash
   python app.py
   ```
   The API defaults to `http://localhost:5000`.

## API Overview

### `GET /api/health`
Returns service status and dataset sizes.

### `GET /api/resources`
Query params: `county`, `type`, `q`, `limit`.

### `GET /api/resources/<id>`
Returns a single resource object by `id`.

### `GET /api/opportunities`
Query params: `county`, `category`, `q`, `limit`.

### `GET /api/opportunities/<id>`
Returns a single opportunity by `id`.

### `GET /api/meta/counties`
List of unique counties represented in the dataset.

### `GET /api/meta/stats`
Aggregated counts by county/type/category to support dashboards.

## Example Requests
```bash
# All Broward therapy resources
curl "http://localhost:5000/api/resources?county=Broward&type=therapy"

# Scholarships and jobs matching the word "tech"
curl "http://localhost:5000/api/opportunities?q=tech"
```

The backend can be deployed independently (Render, Fly.io, etc.) and consumed by the existing static site or any future client.
