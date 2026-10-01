"""
Sovereign Books — Phase 0 MVP product layer.

Built on the substrate demo engines, with real persistence and bank connect.
"""

from .apps_manager import AppsManager
from .bank_service import BankService
from .books_extended import BooksExtended
from .crm_store import CRMStore
from .db import db_session, get_connection, init_db
from .ledger_store import PersistentLedger
from .roadmap_registry import FEATURE_REGISTRY, verify_all

__all__ = [
    "AppsManager",
    "BankService",
    "BooksExtended",
    "CRMStore",
    "FEATURE_REGISTRY",
    "PersistentLedger",
    "db_session",
    "get_connection",
    "init_db",
    "verify_all",
]
