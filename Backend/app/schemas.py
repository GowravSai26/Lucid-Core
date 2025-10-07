from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ------------------------------------------------------------
# ENUMS
# ------------------------------------------------------------
class NodeStatus(str, Enum):
    pending = "pending"
    ok = "ok"
    error = "error"

# ------------------------------------------------------------
# PROJECT SCHEMAS
# ------------------------------------------------------------
class ProjectCreate(BaseModel):
    name: str


class ProjectRead(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True  # replaces orm_mode=True in Pydantic v2


# ------------------------------------------------------------
# NODE SCHEMAS
# ------------------------------------------------------------
class NodeCreate(BaseModel):
    project_id: int
    branch_id: int
    parent_id: Optional[int] = None
    title: Optional[str]
    prompt: Optional[str]


class NodeRead(BaseModel):
    id: int
    project_id: int
    branch_id: int
    parent_id: Optional[int]
    title: Optional[str]
    prompt: Optional[str]
    response_ref: Optional[str]
    status: NodeStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------------------------------------------------
# BRANCH SCHEMAS (used in planner)
# ------------------------------------------------------------
class BranchRead(BaseModel):
    id: int
    project_id: int
    name: Optional[str]
    status: Optional[str]
    head_node_id: Optional[int]

    class Config:
        from_attributes = True


# ------------------------------------------------------------
# PLAN SCHEMAS (for planner route)
# ------------------------------------------------------------
class PlanCreate(BaseModel):
    goal: str


class PlanRead(BaseModel):
    branch_id: int
    total_nodes: int
    nodes: List[NodeRead]
