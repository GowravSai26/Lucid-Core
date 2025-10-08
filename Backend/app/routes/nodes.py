# ---------------------------------------------------------
# 🧠 Node Routes — Create, List, Link, Update
# ---------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from Backend.app.database import get_db
from Backend.app import models

router = APIRouter(prefix="/nodes", tags=["Nodes"])


# ---------------------------------------------------------
# Create a New Node
# ---------------------------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_node(
    project_id: int,
    branch_id: int = None,
    parent_id: int = None,
    title: str = None,
    prompt: str = None,
    response_ref: str = None,
    db: Session = Depends(get_db),
):
    """
    Creates a new reasoning node (prompt-response step) for a given branch or project.
    Each node can have a parent, forming a reasoning tree.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if branch_id:
        branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found.")

    node = models.Node(
        project_id=project_id,
        branch_id=branch_id,
        parent_id=parent_id,
        title=title,
        prompt=prompt,
        response_ref=response_ref,
        status=models.NodeStatus.pending,
    )

    db.add(node)
    db.commit()
    db.refresh(node)
    return {"message": "🧠 Node created successfully", "node_id": node.id}


# ---------------------------------------------------------
# Get All Nodes in a Branch
# ---------------------------------------------------------
@router.get("/branch/{branch_id}")
def get_nodes_in_branch(branch_id: int, db: Session = Depends(get_db)):
    nodes = db.query(models.Node).filter(models.Node.branch_id == branch_id).all()
    if not nodes:
        raise HTTPException(status_code=404, detail="No nodes found in this branch.")
    return {
        "branch_id": branch_id,
        "nodes": [
            {
                "id": n.id,
                "title": n.title,
                "prompt": n.prompt,
                "response_ref": n.response_ref,
                "status": n.status,
                "created_at": n.created_at,
                "parent_id": n.parent_id,
            }
            for n in nodes
        ],
    }


# ---------------------------------------------------------
# Get Node by ID
# ---------------------------------------------------------
@router.get("/{node_id}")
def get_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found.")
    return {
        "id": node.id,
        "title": node.title,
        "prompt": node.prompt,
        "response_ref": node.response_ref,
        "status": node.status,
        "created_at": node.created_at,
        "project_id": node.project_id,
        "branch_id": node.branch_id,
        "parent_id": node.parent_id,
    }


# ---------------------------------------------------------
# Update Node Status or Response
# ---------------------------------------------------------
@router.put("/{node_id}")
def update_node(
    node_id: int,
    status: str = None,
    response_ref: str = None,
    db: Session = Depends(get_db),
):
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found.")

    if status:
        node.status = status
    if response_ref:
        node.response_ref = response_ref

    db.commit()
    db.refresh(node)
    return {"message": "✅ Node updated successfully", "node_id": node.id}


# ---------------------------------------------------------
# Delete a Node
# ---------------------------------------------------------
@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found.")

    db.delete(node)
    db.commit()
    return {"message": "🗑️ Node deleted successfully."}
