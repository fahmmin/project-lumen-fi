"""
Family Storage - Manages family groups and memberships
"""

from typing import List, Optional, Dict
import json
import os
import uuid
import random
import string
from datetime import datetime

from backend.models.family import (
    Family, FamilyCreate, FamilyMember, FamilyRole, FamilyUpdate
)
from backend.utils.logger import logger


class FamilyStorage:
    """Manages family data storage"""

    def __init__(self):
        self.data_dir = "backend/data/families"
        os.makedirs(self.data_dir, exist_ok=True)

        # Index file for quick lookups
        self.index_file = os.path.join(self.data_dir, "_index.json")
        self._ensure_index()

    def _ensure_index(self):
        """Ensure index file exists"""
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w') as f:
                json.dump({
                    "invite_codes": {},  # invite_code -> family_id
                    "user_families": {}  # user_id -> [family_ids]
                }, f, indent=2)

    def _load_index(self) -> Dict:
        """Load index file"""
        with open(self.index_file, 'r') as f:
            return json.load(f)

    def _save_index(self, index: Dict):
        """Save index file"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)

    def _generate_invite_code(self) -> str:
        """Generate unique 6-character invite code"""
        index = self._load_index()

        # Generate code until we find a unique one
        max_attempts = 100
        for _ in range(max_attempts):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

            if code not in index["invite_codes"]:
                return code

        raise ValueError("Failed to generate unique invite code")

    def _get_family_file(self, family_id: str) -> str:
        """Get path to family file"""
        return os.path.join(self.data_dir, f"{family_id}.json")

    def _load_family(self, family_id: str) -> Optional[Family]:
        """Load family from file"""
        file_path = self._get_family_file(family_id)

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)

            # Convert datetime strings
            data['created_at'] = datetime.fromisoformat(data['created_at'])
            for member in data.get('members', []):
                member['joined_at'] = datetime.fromisoformat(member['joined_at'])

            return Family(**data)

    def _save_family(self, family: Family):
        """Save family to file"""
        file_path = self._get_family_file(family.family_id)

        # Convert to dict and handle datetimes
        data = family.model_dump()
        data['created_at'] = data['created_at'].isoformat()
        for member in data.get('members', []):
            member['joined_at'] = member['joined_at'].isoformat()

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def create_family(self, family_data: FamilyCreate) -> Family:
        """Create a new family"""
        family_id = f"family_{uuid.uuid4().hex[:12]}"
        invite_code = self._generate_invite_code()

        # Create family
        family = Family(
            family_id=family_id,
            name=family_data.name,
            invite_code=invite_code,
            created_by=family_data.created_by,
            description=family_data.description,
            shared_budget=family_data.shared_budget,
            members=[
                FamilyMember(
                    user_id=family_data.created_by,
                    role=FamilyRole.ADMIN
                )
            ]
        )

        # Save family
        self._save_family(family)

        # Update index
        index = self._load_index()
        index["invite_codes"][invite_code] = family_id

        if family_data.created_by not in index["user_families"]:
            index["user_families"][family_data.created_by] = []
        index["user_families"][family_data.created_by].append(family_id)

        self._save_index(index)

        logger.info(f"Created family {family_id} with invite code {invite_code}")

        return family

    def get_family_by_id(self, family_id: str) -> Optional[Family]:
        """Get family by ID"""
        return self._load_family(family_id)

    def get_family_by_invite_code(self, invite_code: str) -> Optional[Family]:
        """Get family by invite code"""
        index = self._load_index()
        family_id = index["invite_codes"].get(invite_code.upper())

        if not family_id:
            return None

        return self._load_family(family_id)

    def get_user_families(self, user_id: str) -> List[Family]:
        """Get all families a user belongs to"""
        index = self._load_index()
        family_ids = index["user_families"].get(user_id, [])

        families = []
        for family_id in family_ids:
            family = self._load_family(family_id)
            if family:
                families.append(family)

        return families

    def join_family(self, invite_code: str, user_id: str, display_name: Optional[str] = None) -> Family:
        """Add user to family via invite code"""
        # Get family
        family = self.get_family_by_invite_code(invite_code)

        if not family:
            raise ValueError("Invalid invite code")

        # Check if user already in family
        if any(m.user_id == user_id for m in family.members):
            raise ValueError("User already in family")

        # Add member
        member = FamilyMember(
            user_id=user_id,
            role=FamilyRole.MEMBER,
            display_name=display_name
        )
        family.members.append(member)

        # Save family
        self._save_family(family)

        # Update index
        index = self._load_index()
        if user_id not in index["user_families"]:
            index["user_families"][user_id] = []
        if family.family_id not in index["user_families"][user_id]:
            index["user_families"][user_id].append(family.family_id)
        self._save_index(index)

        logger.info(f"User {user_id} joined family {family.family_id}")

        return family

    def leave_family(self, family_id: str, user_id: str) -> bool:
        """Remove user from family"""
        family = self._load_family(family_id)

        if not family:
            return False

        # Check if user is in family
        member_to_remove = None
        for member in family.members:
            if member.user_id == user_id:
                member_to_remove = member
                break

        if not member_to_remove:
            return False

        # Don't allow admin to leave if there are other members
        if member_to_remove.role == FamilyRole.ADMIN and len(family.members) > 1:
            raise ValueError("Admin cannot leave family with other members. Transfer admin or remove all members first.")

        # Remove member
        family.members.remove(member_to_remove)

        # If no members left, delete family
        if len(family.members) == 0:
            self.delete_family(family_id)
            logger.info(f"Deleted empty family {family_id}")
        else:
            self._save_family(family)

        # Update index
        index = self._load_index()
        if user_id in index["user_families"]:
            if family_id in index["user_families"][user_id]:
                index["user_families"][user_id].remove(family_id)
        self._save_index(index)

        logger.info(f"User {user_id} left family {family_id}")

        return True

    def update_family(self, family_id: str, user_id: str, updates: FamilyUpdate) -> Family:
        """Update family settings (admin only)"""
        family = self._load_family(family_id)

        if not family:
            raise ValueError("Family not found")

        # Check if user is admin
        is_admin = any(m.user_id == user_id and m.role == FamilyRole.ADMIN for m in family.members)

        if not is_admin:
            raise ValueError("Only admin can update family settings")

        # Apply updates
        if updates.name is not None:
            family.name = updates.name
        if updates.description is not None:
            family.description = updates.description
        if updates.shared_budget is not None:
            family.shared_budget = updates.shared_budget

        # Save
        self._save_family(family)

        logger.info(f"Updated family {family_id}")

        return family

    def delete_family(self, family_id: str) -> bool:
        """Delete a family"""
        family = self._load_family(family_id)

        if not family:
            return False

        # Delete file
        file_path = self._get_family_file(family_id)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Update index
        index = self._load_index()

        # Remove invite code
        if family.invite_code in index["invite_codes"]:
            del index["invite_codes"][family.invite_code]

        # Remove from user families
        for member in family.members:
            if member.user_id in index["user_families"]:
                if family_id in index["user_families"][member.user_id]:
                    index["user_families"][member.user_id].remove(family_id)

        self._save_index(index)

        logger.info(f"Deleted family {family_id}")

        return True

    def get_all_families(self) -> List[Family]:
        """Get all families (for admin/stats)"""
        families = []

        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".json") and filename != "_index.json":
                    family_id = filename.replace(".json", "")
                    family = self._load_family(family_id)
                    if family:
                        families.append(family)

        return families


# Global instance
family_storage = FamilyStorage()
