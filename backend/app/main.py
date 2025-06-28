from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import expenses, categories, accounts, incomes, transfers, budgets

app = FastAPI(title="Family Budget API")

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
