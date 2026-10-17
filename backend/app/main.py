from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import accounts, transactions

app = FastAPI(title="FinSight AI API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "FinSight AI API", "version": "0.1.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
