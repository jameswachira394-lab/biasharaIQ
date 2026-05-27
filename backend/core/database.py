from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Build connect_args — force SSL for Render/cloud Postgres
_connect_args = {}
db_url = settings.DATABASE_URL

# Render and most cloud Postgres providers require SSL
if "localhost" not in db_url and "127.0.0.1" not in db_url:
    _connect_args["sslmode"] = "require"

engine = create_engine(
    db_url,
    pool_pre_ping=True,       # Verify connection health before each use
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,         # Recycle connections every 5 min to avoid stale SSL sessions
    pool_timeout=30,          # Wait up to 30s for a connection from the pool
    connect_args=_connect_args,
)


@event.listens_for(engine, "connect")
def on_connect(dbapi_connection, connection_record):
    """Log successful DB connections for debugging."""
    logger.debug("New database connection established")


@event.listens_for(engine, "checkout")
def on_checkout(dbapi_connection, connection_record, connection_proxy):
    """Validate connection on checkout to catch broken SSL sessions early."""
    try:
        dbapi_connection.cursor().execute("SELECT 1")
    except Exception:
        logger.warning("Stale DB connection detected on checkout — discarding")
        raise


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
