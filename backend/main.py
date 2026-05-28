from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from dotenv import load_dotenv
import os
import logging
import time
from datetime import datetime

load_dotenv()

from models.database import engine, get_db
from models.models import Base
from routes.auth import router as auth_router
from routes.email_verification import router as email_verification_router
from routes.transactions import router as transactions_router
from routes.routes import (
    dashboard_router, insights_router, ai_router,
    reports_router, categories_router, profile_router
)
from routes.payments import router as payments_router
from routes.subscriptions import router as subscriptions_router
from routes.uploads import router as uploads_router
from core.config import settings


logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


try:
    Base.metadata.create_all(bind=engine)
    logger.info("[SUCCESS] Database initialized successfully")
except Exception as e:
    logger.error(f"[FAIL] Failed to initialize database: {e}")

app = FastAPI(
    title="BiasharaIQ API",
    description="Financial Intelligence Platform for Kenyan SMEs",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


if not settings.DEBUG:
    from urllib.parse import urlparse
    allowed_hosts = [
        urlparse(o).hostname
        for o in settings.cors_origins_list
        if o and o != "*" and urlparse(o).hostname
    ]
    # Always allow Render's external hostname and subdomains
    render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if render_host:
        allowed_hosts.append(render_host)
    allowed_hosts.append("*.onrender.com")
    
    # Remove duplicates and None values
    allowed_hosts = list(set([h for h in allowed_hosts if h]))
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts
    )


cors_origins = settings.cors_origins_list
logger.info(f"CORS Origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = f"{datetime.now().timestamp()}"
    
    # Log request
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"[{request_id}] Error: {str(e)} - Duration: {process_time:.3f}s")
        raise

# Register routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(email_verification_router, prefix="/auth", tags=["Email Verification"])
app.include_router(transactions_router, tags=["Transactions"])
app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(insights_router, tags=["Insights"])
app.include_router(ai_router, tags=["AI"])
app.include_router(reports_router, tags=["Reports"])
app.include_router(categories_router, tags=["Categories"])
app.include_router(profile_router, tags=["Profile"])
app.include_router(payments_router)
app.include_router(subscriptions_router)
app.include_router(uploads_router)


@app.get("/")
async def root():
    return {
        "name": "BiasharaIQ API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else None
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check including database connectivity"""
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": settings.ENVIRONMENT,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e) if settings.DEBUG else "Database connection failed"
            }
        )

#ma
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for production error responses"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"error": str(exc), "type": type(exc).__name__}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
    