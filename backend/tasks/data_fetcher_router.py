"""
Data Fetcher Router - Main router for dispatching data fetching tasks to specific processors
This file acts as the main entry point and router for all data fetching operations.
"""
from celery import current_task
from celery_app import celery_app
from datetime import datetime
import logging
from typing import Dict, Any

from .processors.prospect_processor import ProspectDataProcessor
from .processors.pkb_processor import PKBDataProcessor
from .processors.parts_inbound_processor import PartsInboundDataProcessor
from .processors.leasing_processor import LeasingDataProcessor
from .processors.document_handling_processor import DocumentHandlingDataProcessor
from .processors.unit_inbound_processor import UnitInboundDataProcessor
from .api_clients import initialize_default_api_configs

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API configurations on module load
try:
    initialize_default_api_configs()
except Exception as e:
    logger.warning(f"Failed to initialize API configs: {e}")


class DataFetcherRouter:
    """Main router for data fetching operations"""
    
    def __init__(self):
        self.processors = {
            "prospect": ProspectDataProcessor(),
            "pkb": PKBDataProcessor(),
            "parts_inbound": PartsInboundDataProcessor(),
            "leasing": LeasingDataProcessor(),
            "doch_read": DocumentHandlingDataProcessor(),
            "uinb_read": UnitInboundDataProcessor()
        }
    
    def get_processor(self, fetch_type: str):
        """Get the appropriate processor for the fetch type"""
        processor = self.processors.get(fetch_type)
        if not processor:
            raise ValueError(f"Unknown fetch type: {fetch_type}")
        return processor
    
    def execute_fetch(self, fetch_type: str, dealer_id: str, from_time: str = None, to_time: str = None, **kwargs) -> Dict[str, Any]:
        """Execute data fetch using the appropriate processor"""
        processor = self.get_processor(fetch_type)
        return processor.execute(dealer_id, from_time, to_time, **kwargs)


# Global router instance
router = DataFetcherRouter()


@celery_app.task(bind=True)
def health_check(self):
    """Health check task"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@celery_app.task(bind=True)
def fetch_prospect_data(self, dealer_id: str, from_time: str = None, to_time: str = None):
    """
    Fetch prospect data for a specific dealer
    """
    try:
        return router.execute_fetch("prospect", dealer_id, from_time, to_time)
    except Exception as e:
        logger.error(f"Prospect data fetch failed for dealer {dealer_id}: {e}")
        # Check if dealer is inactive
        if "inactive" in str(e):
            return {"status": "skipped", "reason": "dealer_inactive"}
        raise


@celery_app.task(bind=True)
def fetch_pkb_data(self, dealer_id: str, from_time: str = None, to_time: str = None):
    """
    Fetch PKB (Service Record) data for a specific dealer
    """
    try:
        return router.execute_fetch("pkb", dealer_id, from_time, to_time)
    except Exception as e:
        logger.error(f"PKB data fetch failed for dealer {dealer_id}: {e}")
        # Check if dealer is inactive
        if "inactive" in str(e):
            return {"status": "skipped", "reason": "dealer_inactive"}
        raise


@celery_app.task(bind=True)
def fetch_parts_inbound_data(self, dealer_id: str, from_time: str = None, to_time: str = None, no_po: str = ""):
    """
    Fetch Parts Inbound data for a specific dealer
    """
    try:
        return router.execute_fetch("parts_inbound", dealer_id, from_time, to_time, no_po=no_po)
    except Exception as e:
        logger.error(f"Parts Inbound data fetch failed for dealer {dealer_id}: {e}")
        # Check if dealer is inactive
        if "inactive" in str(e):
            return {"status": "skipped", "reason": "dealer_inactive"}
        raise


@celery_app.task(bind=True)
def fetch_leasing_data(self, dealer_id: str, from_time: str = None, to_time: str = None, id_spk: str = ""):
    """
    Fetch Leasing requirement data for a specific dealer
    """
    try:
        return router.execute_fetch("leasing", dealer_id, from_time, to_time, id_spk=id_spk)
    except Exception as e:
        logger.error(f"Leasing data fetch failed for dealer {dealer_id}: {e}")
        # Check if dealer is inactive
        if "inactive" in str(e):
            return {"status": "skipped", "reason": "dealer_inactive"}
        raise


@celery_app.task(bind=True)
def fetch_document_handling_data(self, dealer_id: str, from_time: str = None, to_time: str = None,
                                id_spk: str = "", id_customer: str = ""):
    """
    Fetch document handling data for a specific dealer
    """
    try:
        return router.execute_fetch("doch_read", dealer_id, from_time, to_time,
                                  id_spk=id_spk, id_customer=id_customer)
    except Exception as e:
        logger.error(f"Document handling data fetch failed for dealer {dealer_id}: {e}")
        if "inactive" in str(e):
            return {"status": "skipped", "reason": "dealer_inactive"}
        raise


@celery_app.task(bind=True)
def fetch_unit_inbound_data(self, dealer_id: str, from_time: str = None, to_time: str = None,
                           po_id: str = "", no_shipping_list: str = ""):
    """
    Fetch unit inbound data for a specific dealer
    """
    try:
        return router.execute_fetch("uinb_read", dealer_id, from_time, to_time,
                                  po_id=po_id, no_shipping_list=no_shipping_list)
    except Exception as e:
        logger.error(f"Unit inbound data fetch failed for dealer {dealer_id}: {e}")
        if "inactive" in str(e):
            return {"status": "skipped", "reason": "dealer_inactive"}
        raise


# Convenience functions for direct processor access (useful for testing)
def get_prospect_processor() -> ProspectDataProcessor:
    """Get prospect processor instance"""
    return router.get_processor("prospect")


def get_pkb_processor() -> PKBDataProcessor:
    """Get PKB processor instance"""
    return router.get_processor("pkb")


def get_parts_inbound_processor() -> PartsInboundDataProcessor:
    """Get Parts Inbound processor instance"""
    return router.get_processor("parts_inbound")


def get_leasing_processor() -> LeasingDataProcessor:
    """Get Leasing processor instance"""
    return router.get_processor("leasing")


def get_document_handling_processor() -> DocumentHandlingDataProcessor:
    """Get document handling processor instance"""
    return router.get_processor("doch_read")


def get_unit_inbound_processor() -> UnitInboundDataProcessor:
    """Get unit inbound processor instance"""
    return router.get_processor("uinb_read")


# Export the main tasks for backward compatibility
__all__ = [
    'health_check',
    'fetch_prospect_data',
    'fetch_pkb_data',
    'fetch_parts_inbound_data',
    'fetch_leasing_data',
    'fetch_document_handling_data',
    'fetch_unit_inbound_data',
    'router',
    'get_prospect_processor',
    'get_pkb_processor',
    'get_parts_inbound_processor',
    'get_leasing_processor',
    'get_document_handling_processor',
    'get_unit_inbound_processor'
]
