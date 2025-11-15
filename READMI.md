README — BYFORT AI starter

- FastAPI backend (REST + WebSocket)
- Auto-device-account (1 device = 1 account)
- Simple retrieval QA (TF-IDF) with generator
- Static frontend (index.html) with dark blue/black/white theme

Run:
1. pip install -r requirements.txt
2. uvicorn app.main:app --reload --port 8000
3. open http://localhost:8000

Limitations:
- This starter contains a TF-IDF based retrieval QA and dataset generator. It is NOT a full on-device LLM. To integrate large models, you need model binaries or remote API.
