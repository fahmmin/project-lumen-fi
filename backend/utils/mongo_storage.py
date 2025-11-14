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
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        if not settings.MONGO_URI:
            logger.warning("MONGO_URI not set, MongoDB storage disabled")
            return
        
        try:
            self.client = MongoClient(
                settings.MONGO_URI,
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client.get_database('lumen')
            self.audits_collection = self.db.audits
            self.users_collection = self.db.users
            logger.info("Connected to MongoDB successfully")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"MongoDB connection failed: {e}. Continuing without MongoDB.")
            self.client = None
            self.db = None
            self.audits_collection = None
            self.users_collection = None
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            self.client = None
            self.db = None
            self.audits_collection = None
            self.users_collection = None
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        return self.client is not None and self.audits_collection is not None
    
    def register_user(self, user_id: str, wallet_address: Optional[str] = None) -> bool:
        """
        Register a user in MongoDB (auto-called when profile is created)
        
        Args:
            user_id: User ID (wallet address)
            wallet_address: Wallet address (same as user_id typically)
            
        Returns:
            True if registered successfully, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            user_doc = {
                "user_id": user_id,
                "wallet_address": wallet_address or user_id,
                "registered_at": datetime.now(),
                "last_active": datetime.now(),
            }
            
            # Upsert user
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": user_doc, "$setOnInsert": {"created_at": datetime.now()}},
                upsert=True
            )
            logger.info(f"Registered user {user_id} in MongoDB")
            return True
        except Exception as e:
            logger.error(f"Error registering user in MongoDB: {e}")
            return False
    
    def save_audit(self, audit_id: str, audit_report: Dict, amount: float, user_id: Optional[str] = None) -> bool:
        """
        Save audit data to MongoDB
        
        Args:
            audit_id: Audit ID
            audit_report: Full audit report dictionary
            amount: Receipt amount
            user_id: Optional user ID
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            audit_doc = {
                "audit_id": audit_id,
                "user_id": user_id,
                "amount": amount,
                "audit_report": audit_report,
                "timestamp": datetime.now(),
                "vendor": audit_report.get("invoice_data", {}).get("vendor", "Unknown"),
                "date": audit_report.get("invoice_data", {}).get("date", ""),
                "status": audit_report.get("overall_status", "unknown"),
                "category": audit_report.get("invoice_data", {}).get("category", ""),
            }
            
            # Use audit_id as unique identifier (upsert)
            self.audits_collection.update_one(
                {"audit_id": audit_id},
                {"$set": audit_doc},
                upsert=True
            )
            logger.info(f"Saved audit {audit_id} to MongoDB")
            return True
        except Exception as e:
            logger.error(f"Error saving audit to MongoDB: {e}")
            return False
    
    def get_audit(self, audit_id: str) -> Optional[Dict]:
        """Get audit by ID"""
        if not self.is_connected():
            return None
        
        try:
            doc = self.audits_collection.find_one({"audit_id": audit_id})
            if doc:
                # Remove MongoDB _id field
                doc.pop("_id", None)
                return doc
            return None
        except Exception as e:
            logger.error(f"Error getting audit from MongoDB: {e}")
            return None
    
    def get_user_audits(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get all audits for a user"""
        if not self.is_connected():
            return []
        
        try:
            cursor = self.audits_collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            audits = []
            for doc in cursor:
                doc.pop("_id", None)
                audits.append(doc)
            return audits
        except Exception as e:
            logger.error(f"Error getting user audits from MongoDB: {e}")
            return []
    
    def get_all_audits(self, limit: int = 100) -> List[Dict]:
        """Get all audits (for admin/analytics)"""
        if not self.is_connected():
            return []
        
        try:
            cursor = self.audits_collection.find().sort("timestamp", -1).limit(limit)
            
            audits = []
            for doc in cursor:
                doc.pop("_id", None)
                audits.append(doc)
            return audits
        except Exception as e:
            logger.error(f"Error getting all audits from MongoDB: {e}")
            return []
    
    def get_audit_stats(self, user_id: Optional[str] = None) -> Dict:
        """Get audit statistics"""
        if not self.is_connected():
            return {
                "total_audits": 0,
                "total_amount": 0,
                "by_status": {},
                "by_category": {},
                "recent_count": 0
            }
        
        try:
            query = {"user_id": user_id} if user_id else {}
            
            total_audits = self.audits_collection.count_documents(query)
            
            # Calculate total amount
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": None,
                    "total_amount": {"$sum": "$amount"}
                }}
            ]
            amount_result = list(self.audits_collection.aggregate(pipeline))
            total_amount = amount_result[0]["total_amount"] if amount_result else 0
            
            # Count by status
            status_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }}
            ]
            status_counts = {}
            for result in self.audits_collection.aggregate(status_pipeline):
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
            category_counts = {}
            for result in self.audits_collection.aggregate(category_pipeline):
                category_counts[result["_id"]] = {
                    "count": result["count"],
                    "total_amount": result["total_amount"]
                }
            
            # Recent audits (last 30 days)
            from datetime import timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_query = {**query, "timestamp": {"$gte": thirty_days_ago}}
            recent_count = self.audits_collection.count_documents(recent_query)
            
            return {
                "total_audits": total_audits,
                "total_amount": total_amount,
                "by_status": status_counts,
                "by_category": category_counts,
                "recent_count": recent_count
            }
        except Exception as e:
            logger.error(f"Error getting audit stats from MongoDB: {e}")
            return {
                "total_audits": 0,
                "total_amount": 0,
                "by_status": {},
                "by_category": {},
                "recent_count": 0
            }


# Global MongoDB storage instance
_mongo_storage = None


def get_mongo_storage() -> MongoStorage:
    """Get global MongoDB storage instance"""
    global _mongo_storage
    if _mongo_storage is None:
        _mongo_storage = MongoStorage()
    return _mongo_storage

