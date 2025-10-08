from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from Backend.app.database import get_db
from Backend.app import models, schemas

router = APIRouter(prefix="/branches", tags=["branches"])


# ----------------------------------------------------------
# 🧱 Create a new branch (user manually spawns it)
# ----------------------------------------------------------
@router.post("/", response_model=schemas.BranchRead)
def create_branch(branch: schemas.BranchCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == branch.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_branch = models.Branch(
        name=branch.name,
        project_id=branch.project_id,
        base_node_id=branch.base_node_id,
        status="active",
        created_at=datetime.utcnow()
    )

    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return new_branch


# ----------------------------------------------------------
# 📜 List all branches for a project
# ----------------------------------------------------------
@router.get("/project/{project_id}", response_model=list[schemas.BranchRead])
def list_project_branches(project_id: int, db: Session = Depends(get_db)):
    branches = db.query(models.Branch).filter(models.Branch.project_id == project_id).all()
    return branches


# ----------------------------------------------------------
# 🔍 Get specific branch details
# ----------------------------------------------------------
@router.get("/{branch_id}", response_model=schemas.BranchRead)
def get_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


# ----------------------------------------------------------
# 🔄 Merge a branch back into main (simplified logic)
# ----------------------------------------------------------
@router.post("/{branch_id}/merge")
def merge_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # mark branch as merged
    branch.status = "merged"
    db.commit()

    # ✨ Later — you can add:
    # - merge logic to bring node updates into the main branch
    # - RL or revision history capture here

    return {"detail": f"Branch '{branch.name}' successfully merged into main."}


# ----------------------------------------------------------
# ❌ Delete a branch
# ----------------------------------------------------------
@router.delete("/{branch_id}")
def delete_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    db.delete(branch)
    db.commit()
    return {"detail": f"Branch '{branch.name}' deleted successfully."}
