from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import expenses, categories

app = FastAPI(title="Family Budget API")

# Allow dev frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expenses.router)
app.include_router(categories.router)

@app.get("/api/health")
async def health():
    return {"status": "ok"}
