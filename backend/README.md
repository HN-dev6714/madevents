# Backend (FastAPI)

Run the FastAPI backend locally for development.

Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the server:

```bash
uvicorn main:app --reload --port 8000
```
