"""
Shared database utilities for microservices
"""

import os
from typing import Generator
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .logger import setup_logger

logger = setup_logger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dealer_user:dealer_pass@localhost:5432/dealer_dashboard"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables(schema_name: str = None) -> None:
    """
    Create all tables for the specified schema
    
    Args:
        schema_name: Database schema name
    """
    try:
        if schema_name:
            # Set search path for schema
            with engine.connect() as conn:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                conn.execute(text(f"SET search_path TO {schema_name}, public"))
                conn.commit()
        
        Base.metadata.create_all(bind=engine)
        logger.info(f"Tables created successfully for schema: {schema_name or 'default'}")
    except Exception as e:
        logger.error(f"Failed to create tables: {str(e)}")
        raise


def drop_tables(schema_name: str = None) -> None:
    """
    Drop all tables for the specified schema
    
    Args:
        schema_name: Database schema name
    """
    try:
        if schema_name:
            with engine.connect() as conn:
                conn.execute(text(f"SET search_path TO {schema_name}, public"))
                conn.commit()
        
        Base.metadata.drop_all(bind=engine)
        logger.info(f"Tables dropped successfully for schema: {schema_name or 'default'}")
    except Exception as e:
        logger.error(f"Failed to drop tables: {str(e)}")
        raise


class DatabaseManager:
    """Database manager for handling schema-specific operations"""
    
    def __init__(self, schema_name: str):
        self.schema_name = schema_name
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with schema context"""
        db = self.SessionLocal()
        try:
            # Set search path for this session
            db.execute(text(f"SET search_path TO {self.schema_name}, public"))
            yield db
        except Exception as e:
            logger.error(f"Database session error in schema {self.schema_name}: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def create_schema_tables(self) -> None:
        """Create tables for this schema"""
        create_tables(self.schema_name)
    
    def drop_schema_tables(self) -> None:
        """Drop tables for this schema"""
        drop_tables(self.schema_name)


# Health check function
def check_database_health() -> bool:
    """
    Check database connectivity
    
    Returns:
        True if database is healthy, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False
