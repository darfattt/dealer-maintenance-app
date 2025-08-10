"""
Dependencies for customer service
"""

import os
import sys
from sqlalchemy.orm import Session

# Add utils to path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../utils'))
if utils_path not in sys.path:
    sys.path.append(utils_path)

from utils.database import DatabaseManager
from app.config import settings

# Database manager
db_manager = DatabaseManager(settings.db_schema)


def get_db() -> Session:
    """Get database session"""
    db = next(db_manager.get_session())
    try:
        yield db
    finally:
        db.close()