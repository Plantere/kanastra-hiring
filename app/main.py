import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import billing

app = FastAPI(
    title="Kanastra API",
    description="API for processing debts and generating invoices",
    version="1.0.0"
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://kanastra.plantere.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(billing.router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
