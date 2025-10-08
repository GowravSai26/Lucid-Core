# ---------------------------------------------------------
# 🧩 Lucid-Core Models — SQLAlchemy ORM Definitions
# ---------------------------------------------------------
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from Backend.app.database import Base


# ---------------------------------------------------------
# ENUMS
# ---------------------------------------------------------
class NodeStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


# ---------------------------------------------------------
# PROJECT MODEL
# ---------------------------------------------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    nodes = relationship("Node", back_populates="project", cascade="all, delete")
    branches = relationship("Branch", back_populates="project", cascade="all, delete")


# ---------------------------------------------------------
# BRANCH MODEL
# ---------------------------------------------------------
class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    base_node_id = Column(Integer, ForeignKey("nodes.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="branches")
    nodes = relationship("Node", back_populates="branch", cascade="all, delete")


# ---------------------------------------------------------
# NODE MODEL
# ---------------------------------------------------------
class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    parent_id = Column(Integer, ForeignKey("nodes.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(255))
    prompt = Column(Text)
    response_ref = Column(Text)
    status = Column(Enum(NodeStatus), default=NodeStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="nodes")
    branch = relationship("Branch", back_populates="nodes")
    artifacts = relationship("Artifact", back_populates="node", cascade="all, delete")


# ---------------------------------------------------------
# ARTIFACT MODEL
# ---------------------------------------------------------
class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"))
    file_path = Column(String(512))
    file_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    node = relationship("Node", back_populates="artifacts")
