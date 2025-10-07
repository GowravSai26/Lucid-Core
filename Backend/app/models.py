# Backend/app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship, backref
import enum
import datetime

Base = declarative_base()

# -------------------------------------------------------------------
# ENUMS
# -------------------------------------------------------------------
class NodeStatus(str, enum.Enum):
    pending = "pending"
    ok = "ok"
    error = "error"

# -------------------------------------------------------------------
# PROJECT MODEL
# -------------------------------------------------------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    branches = relationship("Branch", back_populates="project", cascade="all, delete-orphan")

# -------------------------------------------------------------------
# BRANCH MODEL
# -------------------------------------------------------------------
class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=True)
    status = Column(String, default="active")
    head_node_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="branches")
    nodes = relationship("Node", back_populates="branch", cascade="all, delete-orphan")

# -------------------------------------------------------------------
# NODE MODEL
# -------------------------------------------------------------------
class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    # 🧩 NEW — Parent/child relationships for Lucid’s branching system
    parent_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)

    title = Column(String, nullable=True)
    prompt = Column(Text, nullable=True)
    response_ref = Column(String, nullable=True)    # S3 key
    artifacts_ref = Column(String, nullable=True)
    output = Column(Text, nullable=True)            # actual model output
    status = Column(Enum(NodeStatus), default=NodeStatus.pending)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    branch = relationship("Branch", back_populates="nodes")

    # Self-referencing relationships for automatic branches
    children = relationship(
        "Node",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Node id={self.id} title={self.title} status={self.status}>"
