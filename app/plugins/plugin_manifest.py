from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import re

class PluginPermission(BaseModel):
    action: str
    resource: str

class PluginManifest(BaseModel):
    id: str = Field(..., pattern=r'^[a-z0-9_-]+$')
    name: str
    version: str
    description: str
    author: str
    license: str
    homepage: Optional[str] = None
    repository: Optional[str] = None
    entrypoint: str
    minimum_engine_version: str
    maximum_engine_version: Optional[str] = None
    dependencies: Dict[str, str] = Field(default_factory=dict)
    permissions: List[PluginPermission] = Field(default_factory=list)
