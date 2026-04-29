
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from models.database import engine
from models.models import Base
from routes.auth import router as auth_router
from routes.transactions import router as transactions_router
from routes.routes import (
    dashboard_router, insights_router, ai_router,
    reports_router, categories_router, profile_router
)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BiasharaIQ API",
    description="Financial Intelligence Platform for Kenyan SMEs",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://biasharaiq.vercel.app", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(dashboard_router)
app.include_router(insights_router)
app.include_router(ai_router)
app.include_router(reports_router)
app.include_router(categories_router)
app.include_router(profile_router)


@app.get("/")
def root():
    return {
        "name": "BiasharaIQ API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
