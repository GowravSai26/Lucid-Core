# ---------------------------------------------------------
# 🌿 Branch Routes — Create, List, Get, Delete
# ---------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from Backend.app.database import get_db
from Backend.app import models

router = APIRouter(prefix="/branches", tags=["Branches"])


# ---------------------------------------------------------
# Create a Branch under a Project
# ---------------------------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_branch(project_id: int, name: str, db: Session = Depends(get_db)):
    """
    Creates a new branch for a given project.
    Example: 'research-path', 'debug-version', 'v2-expansion'
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Prevent duplicate branch names in same project
    existing = (
        db.query(models.Branch)
        .filter(models.Branch.project_id == project_id, models.Branch.name == name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Branch with this name already exists.")

    branch = models.Branch(project_id=project_id, name=name)
    db.add(branch)
    db.commit()
    db.refresh(branch)

    return {"message": "🌿 Branch created successfully", "branch_id": branch.id}


# ---------------------------------------------------------
# List All Branches in a Project
# ---------------------------------------------------------
@router.get("/{project_id}")
def list_branches(project_id: int, db: Session = Depends(get_db)):
    branches = db.query(models.Branch).filter(models.Branch.project_id == project_id).all()
    if not branches:
        raise HTTPException(status_code=404, detail="No branches found for this project.")

    return {
        "project_id": project_id,
        "branches": [
            {"id": b.id, "name": b.name, "status": b.status, "created_at": b.created_at}
            for b in branches
        ],
    }


# ---------------------------------------------------------
# Get a Single Branch
# ---------------------------------------------------------
@router.get("/details/{branch_id}")
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found.")
    return {
        "id": branch.id,
        "name": branch.name,
        "status": branch.status,
        "created_at": branch.created_at,
        "project_id": branch.project_id,
    }


# ---------------------------------------------------------
# Delete a Branch
# ---------------------------------------------------------
@router.delete("/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found.")

    db.delete(branch)
    db.commit()
    return {"message": "🗑️ Branch deleted successfully."}
