from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database import engine, Base
import models as _models  # noqa: F401 — side-effect import, registers tables with Base.metadata
from routers import properties, bookings, chat, ai, safety, forum

Base.metadata.create_all(bind=engine)

app = FastAPI(title="bari.com API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(properties.router, prefix="/api")
app.include_router(bookings.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(safety.router, prefix="/api")
app.include_router(forum.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
