from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class Visibility(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class DocumentPermissions(BaseModel):
    """
    Document-level permissions for the Knowledge & Retrieval platform.
    """
    organization_id: str = Field(..., description="The organization the document belongs to")
    workspace_id: str = Field(..., description="The workspace the document belongs to")
    owner_id: str = Field(..., description="The user ID of the document owner")
    allowed_groups: List[str] = Field(default_factory=list, description="Groups allowed to access the document")
    allowed_users: List[str] = Field(default_factory=list, description="Specific users allowed to access the document")
    visibility: Visibility = Field(default=Visibility.INTERNAL, description="Visibility classification of the document")
    
    def can_access(self, user_id: str, organization_id: str, groups: List[str]) -> bool:
        """
        Check if a user can access this document based on governance rules.
        """
        if self.organization_id != organization_id:
            return False
        
        if self.visibility == Visibility.PUBLIC:
            return True
            
        if self.owner_id == user_id:
            return True
            
        if user_id in self.allowed_users:
            return True
            
        if any(group in self.allowed_groups for group in groups):
            return True
            
        if self.visibility == Visibility.INTERNAL:
            return True
            
        return False
