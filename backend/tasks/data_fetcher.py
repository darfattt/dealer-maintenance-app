"""
Data Fetcher - Main router for data fetching tasks (Refactored for better maintainability)

This file now acts as a simple router that delegates to specific processor modules.
Each API has its own processor module for better separation of concerns and easier maintenance.

Architecture:
- data_fetcher.py (this file): Main router and Celery task definitions
- processors/base_processor.py: Base class with common functionality
- processors/prospect_processor.py: Prospect data processing logic
- processors/pkb_processor.py: PKB data processing logic
- processors/parts_inbound_processor.py: Parts Inbound data processing logic
- processors/leasing_processor.py: Leasing requirement data processing logic
- processors/document_handling_processor.py: Document handling data processing logic
"""

# Import the new modular router
from .data_fetcher_router import (
    health_check,
    fetch_prospect_data,
    fetch_pkb_data,
    fetch_parts_inbound_data,
    fetch_leasing_data,
    fetch_document_handling_data,
    router,
    get_prospect_processor,
    get_pkb_processor,
    get_parts_inbound_processor,
    get_leasing_processor,
    get_document_handling_processor
)

# Re-export all the tasks for backward compatibility
__all__ = [
    'health_check',
    'fetch_prospect_data',
    'fetch_pkb_data',
    'fetch_parts_inbound_data',
    'fetch_leasing_data',
    'fetch_document_handling_data',
    'router',
    'get_prospect_processor',
    'get_pkb_processor',
    'get_parts_inbound_processor',
    'get_leasing_processor',
    'get_document_handling_processor'
]
