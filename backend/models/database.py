from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    if db_user and db_pass and db_host and db_name:
        DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    else:
        # Fallback to local
        DATABASE_URL = "postgresql://localhost/biasharaiq"
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 20))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 10))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Connection pooling configuration
engine_kwargs = {
    "pool_pre_ping": True,  # Test connections before using
    "echo": ENVIRONMENT == "development",  # Log SQL in development
    "pool_size": DB_POOL_SIZE,
    "max_overflow": DB_MAX_OVERFLOW,
    "pool_recycle": 3600,  # Recycle connections after 1 hour
}

# Use QueuePool for better connection management in production
if DATABASE_URL.startswith("postgresql"):
    engine_kwargs["poolclass"] = QueuePool
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        engine_kwargs["connect_args"] = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, **engine_kwargs)

# Log pool events in development
if ENVIRONMENT == "development":
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        logger.debug("Database connection established")
    
    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_conn, connection_record, connection_proxy):
        logger.debug(f"Pool size: {engine.pool.size()}, Checked out: {engine.pool.checkedout()}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Database session generator with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def close_db():
    """Close database engine and dispose of pool"""
    try:
        engine.dispose()
        logger.info("Database connection pool disposed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")