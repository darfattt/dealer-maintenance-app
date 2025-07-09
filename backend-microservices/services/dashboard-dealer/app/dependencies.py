"""
Dependencies for the dashboard-dealer service
"""

import os
import sys
from typing import Generator
from sqlalchemy.orm import Session

# Add parent directory to path for utils import
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if parent_path not in sys.path:
    sys.path.append(parent_path)

from utils.database import DatabaseManager
from app.config import settings

# Database manager
db_manager = DatabaseManager(settings.db_schema)


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = next(db_manager.get_session())
    try:
        yield db
    finally:
        db.close()
