from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str

class ProjectRead(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True

class NodeCreate(BaseModel):
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
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
