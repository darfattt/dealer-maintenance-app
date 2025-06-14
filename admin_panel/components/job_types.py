"""
Job Type Mappings
Defines the mapping between job codes (used in API) and labels (displayed in UI)
"""

from typing import Dict, List, Tuple

# Job type mapping: code -> label
JOB_TYPE_MAPPING = {
    "prospect": "Prospect",
    "pkb": "Manage WO - PKB",
    "parts_inbound": "Part Inbound - PINB",
    "leasing": "Handle Leasing Requirement",
    "doch_read": "Manage Document Handling",
    "uinb_read": "Unit Inbound from Purchase Order",
    "bast_read": "Manage Delivery Process",
    "inv1_read": "Manage Billing Process",
    "mdinvh1_read": "Unit Invoice (MD to Dealer)",
    "prsl_read": "Manage Parts Sales",
    "dphlo_read": "DP HLO",
    "inv2_read": "Nota Jasa Bengkel & Nota Suku Cadang",
    "unpaidhlo_read": "Manage Document Handling",
    "mdinvh3_read": "Parts Invoice (MD to Dealer)"
}

# Reverse mapping: label -> code
LABEL_TO_CODE_MAPPING = {v: k for k, v in JOB_TYPE_MAPPING.items()}


def get_job_type_options() -> List[str]:
    """Get list of job type labels for UI display"""
    return list(JOB_TYPE_MAPPING.values())


def get_job_type_codes() -> List[str]:
    """Get list of job type codes for API calls"""
    return list(JOB_TYPE_MAPPING.keys())


def get_job_type_pairs() -> List[Tuple[str, str]]:
    """Get list of (code, label) pairs"""
    return list(JOB_TYPE_MAPPING.items())


def code_to_label(code: str) -> str:
    """Convert job type code to display label"""
    return JOB_TYPE_MAPPING.get(code, code)


def label_to_code(label: str) -> str:
    """Convert job type label to API code"""
    return LABEL_TO_CODE_MAPPING.get(label, label)


def get_codes_from_labels(labels: List[str]) -> List[str]:
    """Convert list of labels to list of codes"""
    return [label_to_code(label) for label in labels]


def get_labels_from_codes(codes: List[str]) -> List[str]:
    """Convert list of codes to list of labels"""
    return [code_to_label(code) for code in codes]


# For backward compatibility and easy access
JOB_TYPES = JOB_TYPE_MAPPING
JOB_TYPE_LABELS = get_job_type_options()
JOB_TYPE_CODES = get_job_type_codes()
