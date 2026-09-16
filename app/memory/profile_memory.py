"""
Profile Memory (Tier 4): User Preferences, Style, and Personalization Traits
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class UserProfile:
    def __init__(
        self,
        user_id: str,
        preferred_language: str = "python",
        preferred_framework: str = "fastapi",
        communication_style: str = "concise",
        interests: Optional[List[str]] = None,
        custom_attributes: Optional[Dict[str, Any]] = None,
    ):
        self.user_id = user_id
        self.preferred_language = preferred_language
        self.preferred_framework = preferred_framework
        self.communication_style = communication_style
        self.interests = interests or []
        self.custom_attributes = custom_attributes or {}
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "preferred_language": self.preferred_language,
            "preferred_framework": self.preferred_framework,
            "communication_style": self.communication_style,
            "interests": self.interests,
            "custom_attributes": self.custom_attributes,
            "updated_at": self.updated_at,
        }


class ProfileMemory:
    """Manages long-term user profile settings, personalization preferences, and traits."""

    def __init__(self):
        self._profiles: Dict[str, UserProfile] = {}

    def create_profile(self, user_id: str, profile_data: Optional[Dict[str, Any]] = None) -> UserProfile:
        data = profile_data or {}
        profile = UserProfile(
            user_id=user_id,
            preferred_language=data.get("preferred_language", "python"),
            preferred_framework=data.get("preferred_framework", "fastapi"),
            communication_style=data.get("communication_style", "concise"),
            interests=data.get("interests", []),
            custom_attributes=data.get("custom_attributes", {}),
        )
        self._profiles[user_id] = profile
        return profile

    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        profile = self._profiles.get(user_id)
        if not profile:
            profile = self.create_profile(user_id, profile_data)
        else:
            if "preferred_language" in profile_data:
                profile.preferred_language = profile_data["preferred_language"]
            if "preferred_framework" in profile_data:
                profile.preferred_framework = profile_data["preferred_framework"]
            if "communication_style" in profile_data:
                profile.communication_style = profile_data["communication_style"]
            if "interests" in profile_data:
                profile.interests = profile_data["interests"]
            if "custom_attributes" in profile_data:
                profile.custom_attributes.update(profile_data["custom_attributes"])
            profile.updated_at = datetime.now(timezone.utc).isoformat()
        return profile

    def get_profile(self, user_id: str) -> UserProfile:
        if user_id not in self._profiles:
            # Default fallback profile
            return self.create_profile(user_id)
        return self._profiles[user_id]

    def delete_profile(self, user_id: str) -> bool:
        if user_id in self._profiles:
            del self._profiles[user_id]
            return True
        return False
