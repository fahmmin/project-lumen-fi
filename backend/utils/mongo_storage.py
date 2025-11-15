"""
MongoDB Storage for Audit Data
Stores audit reports, audit IDs, and amounts in MongoDB
"""

from typing import Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend.config import settings
from backend.utils.logger import logger

class MongoStorage:
    """MongoDB storage for audit data"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.audits_collection = None
        self.users_collection = None
        logger.debug("[MongoDB] __init__ called on MongoStorage, initializing connection objects to None")
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        logger.info(f"[MongoDB] Attempting to connect - MONGO_URI set: {bool(settings.MONGO_URI)}")
        logger.debug(f"[MongoDB][DEBUG] Full MONGO_URI: {settings.MONGO_URI}")
        if not settings.MONGO_URI:
            logger.warning("[MongoDB] MONGO_URI not set, MongoDB storage disabled")
            return
        
        try:
            logger.debug(f"[MongoDB] Connecting to: {settings.MONGO_URI[:20]}...")
            self.client = MongoClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            logger.debug("[MongoDB] Testing connection with ping...")
            self.client.admin.command('ping')
            logger.debug("[MongoDB] Ping successful, retrieving 'lumen' database")
            self.db = self.client.get_database('lumen')
            self.audits_collection = self.db.audits
            self.users_collection = self.db.users
            logger.info("[MongoDB] Connected to MongoDB successfully")
            logger.debug(
                f"[MongoDB][DEBUG] Database info: {{'name': {self.db.name}, "
                f"'audits_collection': {str(self.audits_collection)}, "
                f"'users_collection': {str(self.users_collection)}}}"
            )
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"[MongoDB] Connection failed: {e}. Continuing without MongoDB.")
            logger.debug(f"[MongoDB][DEBUG] Exception in _connect: {repr(e)}")
            self.client = None
            self.db = None
            self.audits_collection = None
            self.users_collection = None
        except Exception as e:
            logger.error(f"[MongoDB] Error connecting to MongoDB: {e}", exc_info=True)
            logger.debug(f"[MongoDB][DEBUG] Exception in _connect (generic): {repr(e)}")
            self.client = None
            self.db = None
            self.audits_collection = None
            self.users_collection = None
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        logger.debug(f"[MongoDB] is_connected() called - result: {self.client is not None and self.audits_collection is not None}")
        return self.client is not None and self.audits_collection is not None
    
    def register_user(self, user_id: str, wallet_address: Optional[str] = None) -> bool:
        """
        Register a user in MongoDB (auto-called when profile is created)
        """
        logger.debug(f"[MongoDB] register_user(user_id={user_id}, wallet_address={wallet_address}) called")
        if not self.is_connected():
            logger.warning("[MongoDB] register_user called but storage not connected")
            return False
        
        try:
            now = datetime.now()
            user_doc = {
                "user_id": user_id,
                "wallet_address": wallet_address or user_id,
                "registered_at": now,
                "last_active": now,
            }
            logger.debug(f"[MongoDB] register_user user_doc to be upserted: {user_doc}")
            
            result = self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": user_doc, "$setOnInsert": {"created_at": now}},
                upsert=True
            )
            logger.info(f"[MongoDB] Registered user {user_id} in MongoDB (matched: {result.matched_count}, modified: {result.modified_count}, upserted_id: {result.upserted_id})")
            logger.debug(f"[MongoDB] register_user returned acknowledged={result.acknowledged}")
            try:
                verify_user = self.users_collection.find_one({"user_id": user_id})
                logger.debug(f"[MongoDB] register_user verification lookup: exists={bool(verify_user)}, doc={verify_user}")
            except Exception as lookup_exc:
                logger.warning(f"[MongoDB] Error during register_user verification: {lookup_exc}")
            return True
        except Exception as e:
            logger.error(f"Error registering user in MongoDB: {e}", exc_info=True)
            logger.debug(f"[MongoDB][DEBUG] register_user EXCEPTION: {repr(e)}")
            return False
    
    def save_audit(self, audit_id: str, audit_report: Dict, amount: float, user_id: Optional[str] = None) -> bool:
        """
        Save audit data to MongoDB
        """
        logger.debug(f"[MongoDB] save_audit called - incoming user_id: {user_id}")
        if user_id:
            user_id = user_id.lower().strip()
            logger.debug(f"[MongoDB] save_audit normalized user_id: '{user_id}'")
            if not user_id:
                user_id = None

        logger.info(f"[MongoDB] save_audit called - audit_id: {audit_id}, user_id: {user_id}, amount: {amount}")
        logger.debug(f"[MongoDB][DEBUG] save_audit - audit_report keys: {list(audit_report.keys()) if hasattr(audit_report, 'keys') else str(audit_report)}")
        if not self.is_connected():
            logger.warning(f"[MongoDB] Not connected - cannot save audit {audit_id}")
            return False
        
        if not user_id:
            logger.warning(f"[MongoDB] WARNING: user_id is None for audit {audit_id}. Audit will be saved without user association.")
        
        try:
            invoice_data = audit_report.get("invoice_data", {})
            vendor = invoice_data.get("vendor", "Unknown")
            date = invoice_data.get("date", "")
            status = audit_report.get("overall_status", "unknown")
            category = invoice_data.get("category", "")
            
            logger.debug(
                f"[MongoDB] Extracted fields - vendor: {vendor!r}, date: {date!r}, "
                f"status: {status!r}, category: {category!r}, "
                f"audit_id: {audit_id!r}, amount: {amount!r}, user_id: {user_id!r}"
            )
            
            audit_doc = {
                "audit_id": audit_id,
                "user_id": user_id,  # Will be None if not provided, but normalized if provided
                "amount": amount,
                "audit_report": audit_report,  # Store full audit report
                "timestamp": datetime.now(),
                "vendor": vendor,
                "date": date,
                "status": status,
                "category": category,
            }
            
            logger.debug(f"[MongoDB] Prepared audit document with keys: {list(audit_doc.keys())}. Full doc: {audit_doc}")

            result = self.audits_collection.update_one(
                {"audit_id": audit_id},
                {"$set": audit_doc},
                upsert=True
            )
            logger.info(
                f"[MongoDB] Saved audit {audit_id} to MongoDB - matched: {result.matched_count}, modified: {result.modified_count}, upserted_id: {result.upserted_id}"
            )
            logger.debug(f"[MongoDB] update_one result raw: {vars(result) if hasattr(result, '__dict__') else str(result)}")
            
            verify_doc = self.audits_collection.find_one({"audit_id": audit_id})
            logger.debug(f"[MongoDB] save_audit verification: found document: {verify_doc is not None}")
            if verify_doc:
                logger.debug(f"[MongoDB] save_audit verify_doc content: {verify_doc}")
                logger.info(f"[MongoDB] Verified audit {audit_id} exists in MongoDB")
                return True
            else:
                logger.error(f"[MongoDB] Verification failed - audit {audit_id} not found after save")
                return False
                
        except Exception as e:
            logger.error(f"[MongoDB] Error saving audit {audit_id} to MongoDB: {e}", exc_info=True)
            logger.debug(f"[MongoDB][DEBUG] save_audit EXCEPTION: {repr(e)}")
            return False
    
    def get_audit(self, audit_id: str) -> Optional[Dict]:
        """Get audit by ID"""
        logger.debug(f"[MongoDB] get_audit called - audit_id: {audit_id}")
        if not self.is_connected():
            logger.warning("[MongoDB] get_audit called but not connected")
            return None
        
        try:
            doc = self.audits_collection.find_one({"audit_id": audit_id})
            logger.debug(f"[MongoDB] get_audit raw doc: {doc}")
            if doc:
                doc.pop("_id", None)
                logger.debug(f"[MongoDB] get_audit removed _id. Final doc: {doc}")
                return doc
            logger.info(f"[MongoDB] get_audit did not find doc for audit_id: {audit_id}")
            return None
        except Exception as e:
            logger.error(f"[MongoDB] Error getting audit from MongoDB: {e}", exc_info=True)
            logger.debug(f"[MongoDB][DEBUG] get_audit EXCEPTION: {repr(e)}")
            return None
    
    def get_user_audits(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get all audits for a user"""
        logger.debug(f"[MongoDB] get_user_audits called - user_id: {user_id}, limit: {limit}")
        if not self.is_connected():
            logger.warning("[MongoDB] get_user_audits called but not connected")
            return []
        
        if user_id:
            user_id = user_id.lower().strip()
            logger.debug(f"[MongoDB] get_user_audits normalized user_id: {user_id}")
        
        try:
            logger.debug(f"[MongoDB] Querying audits for user_id: {user_id}")
            cursor = self.audits_collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            audits = []
            docs_returned = 0
            for doc in cursor:
                doc.pop("_id", None)
                audits.append(doc)
                docs_returned += 1
                logger.debug(f"[MongoDB] get_user_audits - Appended doc, current count: {docs_returned}")
            
            logger.info(f"[MongoDB] Found {len(audits)} audits for user_id: {user_id}")
            logger.debug(f"[MongoDB] get_user_audits - returned audits: {audits}")
            return audits
        except Exception as e:
            logger.error(f"[MongoDB] Error getting user audits from MongoDB: {e}", exc_info=True)
            logger.debug(f"[MongoDB][DEBUG] get_user_audits EXCEPTION: {repr(e)}")
            return []
    
    def get_all_audits(self, limit: int = 100) -> List[Dict]:
        """Get all audits (for admin/analytics)"""
        logger.debug(f"[MongoDB] get_all_audits called with limit={limit}")
        if not self.is_connected():
            logger.warning("[MongoDB] get_all_audits called but not connected")
            return []
        
        try:
            cursor = self.audits_collection.find().sort("timestamp", -1).limit(limit)
            audits = []
            docs_returned = 0
            for doc in cursor:
                doc.pop("_id", None)
                audits.append(doc)
                docs_returned += 1
                logger.debug(f"[MongoDB] get_all_audits - Appended doc, current count: {docs_returned}")
            logger.debug(f"[MongoDB] get_all_audits - Audit docs returned: {audits}")
            return audits
        except Exception as e:
            logger.error(f"Error getting all audits from MongoDB: {e}", exc_info=True)
            logger.debug(f"[MongoDB][DEBUG] get_all_audits EXCEPTION: {repr(e)}")
            return []
    
    def get_audit_stats(self, user_id: Optional[str] = None) -> Dict:
        """Get audit statistics"""
        logger.debug(f"[MongoDB] get_audit_stats called - user_id: {user_id}")
        if not self.is_connected():
            logger.warning("[MongoDB] get_audit_stats called but not connected")
            return {
                "total_audits": 0,
                "total_amount": 0,
                "by_status": {},
                "by_category": {},
                "recent_count": 0
            }
        
        # Normalize user_id to lowercase
        if user_id:
            user_id = user_id.lower().strip()
            logger.debug(f"[MongoDB] get_audit_stats normalized user_id: {user_id}")
        
        try:
            query = {"user_id": user_id} if user_id else {}
            logger.debug(f"[MongoDB] Getting audit stats with query: {query}")
            
            total_audits = self.audits_collection.count_documents(query)
            logger.debug(f"[MongoDB] get_audit_stats total audits: {total_audits}")
            
            # Calculate total amount
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": None,
                    "total_amount": {"$sum": "$amount"}
                }}
            ]
            logger.debug(f"[MongoDB] get_audit_stats amount aggregation pipeline: {pipeline}")
            amount_result = list(self.audits_collection.aggregate(pipeline))
            logger.debug(f"[MongoDB] get_audit_stats amount_result: {amount_result}")
            total_amount = amount_result[0]["total_amount"] if amount_result else 0
            
            # Count by status
            status_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ]
            logger.debug(f"[MongoDB] get_audit_stats status_pipeline: {status_pipeline}")
            status_counts = {}
            status_aggr_results = list(self.audits_collection.aggregate(status_pipeline))
            logger.debug(f"[MongoDB] get_audit_stats status_aggr_results: {status_aggr_results}")
            for result in status_aggr_results:
                status_counts[result["_id"]] = result["count"]
            
            # Count by category
            category_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$amount"}
                }}
            ]
            logger.debug(f"[MongoDB] get_audit_stats category_pipeline: {category_pipeline}")
            category_counts = {}
            category_aggr_results = list(self.audits_collection.aggregate(category_pipeline))
            logger.debug(f"[MongoDB] get_audit_stats category_aggr_results: {category_aggr_results}")
            for result in category_aggr_results:
                category_counts[result["_id"]] = {
                    "count": result["count"],
                    "total_amount": result["total_amount"]
                }
            
            # Recent audits (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_query = {**query, "timestamp": {"$gte": thirty_days_ago}}
            logger.debug(f"[MongoDB] get_audit_stats recent_query: {recent_query}")
            recent_count = self.audits_collection.count_documents(recent_query)
            logger.debug(
                f"[MongoDB] get_audit_stats summary - total_audits: {total_audits}, total_amount: {total_amount}, "
                f"status_counts: {status_counts}, category_counts: {category_counts}, recent_count: {recent_count}"
            )
            return {
                "total_audits": total_audits,
                "total_amount": total_amount,
                "by_status": status_counts,
                "by_category": category_counts,
                "recent_count": recent_count
            }
        except Exception as e:
            logger.error(f"Error getting audit stats from MongoDB: {e}", exc_info=True)
            logger.debug(f"[MongoDB][DEBUG] get_audit_stats EXCEPTION: {repr(e)}")
            return {
                "total_audits": 0,
                "total_amount": 0,
                "by_status": {},
                "by_category": {},
                "recent_count": 0
            }


# Global MongoDB storage instance
_mongo_storage = None
logger.debug("[MongoDB] Global _mongo_storage set to None on module load")

def get_mongo_storage() -> MongoStorage:
    """Get global MongoDB storage instance"""
    global _mongo_storage
    logger.debug("[MongoDB] get_mongo_storage() called")
    if _mongo_storage is None:
        logger.debug("[MongoDB] _mongo_storage is None. Creating new MongoStorage instance.")
        _mongo_storage = MongoStorage()
    else:
        logger.debug("[MongoDB] _mongo_storage already exists.")
    return _mongo_storage

