# Backend (FastAPI)

Run the FastAPI backend locally for development.

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Start the server:

```bash
uvicorn backend.main:app --reload --port 8000
```
