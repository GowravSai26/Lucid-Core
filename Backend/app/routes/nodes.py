from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from rq import Queue
from Backend.app.database import get_db
from Backend.app import models, schemas
from Backend.utils.llm_router import call_chat_completion
from Backend.utils.redis_connection import get_redis_connection
from Backend.app.orchestration import planner, executor
from datetime import datetime

router = APIRouter(prefix="/nodes", tags=["nodes"])

# ---------------------------------------------------------------------
# Create a new node (normal user node)
# ---------------------------------------------------------------------
@router.post("/", response_model=schemas.NodeRead)
def create_node(node: schemas.NodeCreate, db: Session = Depends(get_db)):
    """
    Create a new node under a project branch.
    """
    project = db.query(models.Project).filter(models.Project.id == node.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    branch = db.query(models.Branch).filter(models.Branch.id == node.branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    new_node = models.Node(
        project_id=node.project_id,
        branch_id=node.branch_id,
        parent_id=node.parent_id,
        title=node.title,
        prompt=node.prompt,
        status=models.NodeStatus.pending,
        created_at=datetime.utcnow()
    )
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node


# ---------------------------------------------------------------------
# Run a node (background execution through Redis + executor.py)
# ---------------------------------------------------------------------
@router.post("/{node_id}/run")
def run_node(node_id: int, db: Session = Depends(get_db)):
    """
    Enqueues node execution to Redis queue for background processing.
    Returns instantly while the worker handles the job asynchronously.
    """
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    redis_conn = get_redis_connection()
    q = Queue("lucid_queue", connection=redis_conn)

    job = q.enqueue(executor.execute_node, node_id)


    return {
        "status": "queued",
        "node_id": node.id,
        "job_id": job.id,
        "message": "Node execution started in background."
    }


# ---------------------------------------------------------------------
# Retrieve a node (optional)
# ---------------------------------------------------------------------
@router.get("/{node_id}", response_model=schemas.NodeRead)
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node
