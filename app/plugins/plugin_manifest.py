import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


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
    minimum_engine_version: str = "1.0.0"
    maximum_engine_version: Optional[str] = None
    dependencies: Dict[str, str] = Field(default_factory=dict)
    permissions: List[PluginPermission] = Field(default_factory=list)

    @classmethod
    def parse_manifest_dict(cls, data: Dict[str, Any]) -> "PluginManifest":
        return cls(**data)

    @classmethod
    def parse_manifest_file(cls, filepath: str) -> "PluginManifest":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.parse_manifest_dict(data)
