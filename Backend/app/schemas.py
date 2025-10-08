from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from Backend.app.models import NodeStatus

# ------------------------------------------------
# Project Schemas
# ------------------------------------------------

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------------------------------------
# Branch Schemas
# ------------------------------------------------

class BranchCreate(BaseModel):
    name: str
    project_id: int
    base_node_id: Optional[int] = None


class BranchRead(BaseModel):
    id: int
    name: str
    project_id: int
    base_node_id: Optional[int]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------------------------------------
# Node Schemas
# ------------------------------------------------

class NodeCreate(BaseModel):
    project_id: int
    branch_id: Optional[int] = None
    parent_id: Optional[int] = None
    title: Optional[str]
    prompt: Optional[str]


class NodeRead(BaseModel):
    id: int
    project_id: int
    branch_id: Optional[int]
    parent_id: Optional[int]
    title: Optional[str]
    prompt: Optional[str]
    response_ref: Optional[str]
    status: NodeStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------------------------------------
# Artifact Schemas
# ------------------------------------------------

class ArtifactRead(BaseModel):
    id: int
    node_id: int
    file_path: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True
