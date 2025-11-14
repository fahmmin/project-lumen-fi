"""
PROJECT LUMEN - Seed Data Script
Creates dummy user and test receipts for demo/testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.utils.user_storage import get_user_storage
from backend.models.user import UserProfileCreate
from backend.models.goal import GoalCreate
from backend.rag.vector_store import get_vector_store
from backend.rag.chunker import chunk_document
from backend.rag.retriever import index_documents
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import random
import uuid


def create_test_user():
    """Create a test user profile"""
    print("Creating test user...")

    storage = get_user_storage()

    user_data = UserProfileCreate(
        user_id="test_user_001",
        name="John Doe",
        email="john.doe@example.com",
        salary_monthly=5000.00,
        currency="USD",
        budget_categories={
            "groceries": 500,
            "dining": 350,
            "rent": 1500,
            "utilities": 200,
            "transportation": 300,
            "entertainment": 200,
            "shopping": 250,
            "healthcare": 100
        }
    )

    try:
        profile = storage.create_profile(user_data)
        print(f"✅ Created user: {profile.user_id}")
        return profile.user_id
    except FileExistsError:
        print(f"✅ User already exists: test_user_001")
        return "test_user_001"


def create_test_goals(user_id):
    """Create test financial goals"""
    print("Creating test goals...")

    storage = get_user_storage()

    goals = [
        {
            "name": "Buy a Car",
            "target_amount": 30000.00,
            "target_date": date.today() + relativedelta(years=4),
            "current_savings": 3500.00,
            "priority": "high"
        },
        {
            "name": "Emergency Fund",
            "target_amount": 15000.00,
            "target_date": date.today() + relativedelta(years=2),
            "current_savings": 4500.00,
            "priority": "critical"
        },
        {
            "name": "Vacation to Europe",
            "target_amount": 5000.00,
            "target_date": date.today() + relativedelta(months=10),
            "current_savings": 1200.00,
            "priority": "medium"
        }
    ]

    for goal_data in goals:
        goal = GoalCreate(user_id=user_id, **goal_data)
        created_goal = storage.create_goal(goal)
        print(f"✅ Created goal: {created_goal.name}")


def create_dummy_receipts(user_id):
    """Create dummy receipt data for testing"""
    print("Creating dummy receipts...")

    # Receipt templates
    receipts = [
        # Groceries (monthly pattern)
        *[{
            "vendor": "Whole Foods",
            "category": "groceries",
            "amount": random.uniform(120, 180),
            "date": (date.today() - relativedelta(months=i)).replace(day=random.randint(8, 12)),
            "items": ["Organic Vegetables", "Fruits", "Dairy Products", "Meat"]
        } for i in range(6)],

        # Dining out (frequent)
        *[{
            "vendor": random.choice(["Chipotle", "Olive Garden", "Starbucks", "Panera Bread"]),
            "category": "dining",
            "amount": random.uniform(15, 65),
            "date": date.today() - timedelta(days=random.randint(1, 180)),
            "items": ["Food & Beverages"]
        } for _ in range(25)],

        # Rent (monthly)
        *[{
            "vendor": "Apartment Complex",
            "category": "rent",
            "amount": 1500.00,
            "date": (date.today() - relativedelta(months=i)).replace(day=1),
            "items": ["Monthly Rent"]
        } for i in range(6)],

        # Utilities (monthly)
        *[{
            "vendor": random.choice(["Electric Company", "Gas Company", "Water Department"]),
            "category": "utilities",
            "amount": random.uniform(80, 150),
            "date": (date.today() - relativedelta(months=i)).replace(day=random.randint(15, 20)),
            "items": ["Utility Service"]
        } for i in range(6)],

        # Transportation
        *[{
            "vendor": random.choice(["Shell Gas Station", "Chevron", "Uber", "Lyft"]),
            "category": "transportation",
            "amount": random.uniform(25, 80),
            "date": date.today() - timedelta(days=random.randint(1, 180)),
            "items": ["Transportation"]
        } for _ in range(20)],

        # Entertainment
        *[{
            "vendor": random.choice(["Netflix", "Spotify", "AMC Theaters", "Concert Venue"]),
            "category": "entertainment",
            "amount": random.uniform(10, 120),
            "date": date.today() - timedelta(days=random.randint(1, 180)),
            "items": ["Entertainment"]
        } for _ in range(15)],

        # Shopping
        *[{
            "vendor": random.choice(["Amazon", "Target", "Best Buy", "Macy's"]),
            "category": "shopping",
            "amount": random.uniform(30, 250),
            "date": date.today() - timedelta(days=random.randint(1, 180)),
            "items": ["Clothing", "Electronics", "Home Goods"]
        } for _ in range(18)],

        # Subscriptions (recurring)
        *[{
            "vendor": "Netflix",
            "category": "entertainment",
            "amount": 15.99,
            "date": (date.today() - relativedelta(months=i)).replace(day=15),
            "items": ["Monthly Subscription"]
        } for i in range(8)],

        *[{
            "vendor": "Spotify Premium",
            "category": "entertainment",
            "amount": 9.99,
            "date": (date.today() - relativedelta(months=i)).replace(day=5),
            "items": ["Monthly Subscription"]
        } for i in range(8)],

        # Healthcare
        *[{
            "vendor": "CVS Pharmacy",
            "category": "healthcare",
            "amount": random.uniform(20, 150),
            "date": date.today() - timedelta(days=random.randint(1, 180)),
            "items": ["Medications", "Health Products"]
        } for _ in range(8)],
    ]

    # Index all receipts
    for receipt in receipts:
        document_id = f"doc_{uuid.uuid4().hex[:12]}"

        # Create text content
        text = f"""
        RECEIPT

        Vendor: {receipt['vendor']}
        Date: {receipt['date']}
        Category: {receipt['category']}

        Items:
        {chr(10).join('- ' + item for item in receipt['items'])}

        Total: ${receipt['amount']:.2f}
        """

        # Create metadata
        metadata = {
            "document_id": document_id,
            "user_id": user_id,
            "vendor": receipt['vendor'],
            "date": receipt['date'].isoformat(),
            "amount": receipt['amount'],
            "category": receipt['category'],
            "invoice_number": f"INV-{random.randint(1000, 9999)}"
        }

        # Chunk and index
        chunks = chunk_document(text, metadata=metadata)
        index_documents(chunks)

    print(f"✅ Created and indexed {len(receipts)} dummy receipts")


def main():
    """Run seed data script"""
    print("=" * 60)
    print("PROJECT LUMEN - Seed Data Script")
    print("=" * 60)

    # Create user
    user_id = create_test_user()

    # Create goals
    create_test_goals(user_id)

    # Create receipts
    create_dummy_receipts(user_id)

    print("=" * 60)
    print("✅ SEED DATA COMPLETE!")
    print("=" * 60)
    print(f"\nTest User ID: {user_id}")
    print(f"Test User Email: john.doe@example.com")
    print(f"Total Receipts: ~140 receipts over 6 months")
    print(f"Total Goals: 3 goals")
    print("\nYou can now test the APIs with this user!")
    print("=" * 60)


if __name__ == "__main__":
    main()
