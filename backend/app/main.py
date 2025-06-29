from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import expenses, categories, accounts, incomes, transfers, budgets

import logging, time
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = FastAPI(title="Family Budget API")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response: Response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        logging.info("%s %s -> %d %.1fms", request.method, request.url.path, response.status_code, duration_ms)
        return response

app.add_middleware(LoggingMiddleware)

from .database import engine, Base

@app.on_event("startup")
async def on_startup():
    # Ensure all DB tables exist
    import asyncio, logging
    for attempt in range(10):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logging.info("DB connected and tables ensured")
            break
        except Exception as e:
            logging.warning("DB not ready (%s), retry %d/10", e, attempt+1)
            await asyncio.sleep(2)

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
app.include_router(accounts.router)
app.include_router(incomes.router)
app.include_router(transfers.router)
app.include_router(budgets.router)

@app.get("/api/health")
async def health():
    return {"status": "ok"}
