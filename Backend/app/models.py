from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship
import enum, datetime

Base = declarative_base()

class NodeStatus(str, enum.Enum):
    pending = "pending"
    ok = "ok"
    error = "error"

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    branches = relationship("Branch", back_populates="project", cascade="all, delete-orphan")

class Branch(Base):
    __tablename__ = "branches"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=True)
    status = Column(String, default="active")
    head_node_id = Column(Integer, nullable=True)

    project = relationship("Project", back_populates="branches")
    nodes = relationship("Node", back_populates="branch", cascade="all, delete-orphan")

class Node(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)
    title = Column(String, nullable=True)
    prompt = Column(Text, nullable=True)
    response_ref = Column(String, nullable=True)    # S3 key
    artifacts_ref = Column(String, nullable=True)
    status = Column(Enum(NodeStatus), default=NodeStatus.pending)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    branch = relationship("Branch", back_populates="nodes")
