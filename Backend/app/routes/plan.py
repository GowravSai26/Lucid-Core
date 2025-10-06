from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..orchestration import planner
from ..worker import jobs

router = APIRouter(prefix="/projects/{project_id}", tags=["plan"])

@router.post("/plan")
def create_plan(project_id: int, goal: dict, db: Session = Depends(get_db)):
    """
    Accepts JSON like {"goal": "Build a FastAPI REST service with users"}
    Schedules planner job which will create Node rows for Steps.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    goal_text = goal.get("goal") if isinstance(goal, dict) else str(goal)
    # enqueue planner job (async). For simplicity we call planner synchronously here.
    # Prefer queue.enqueue(planner.generate_plan_job, ...)
    nodes = planner.generate_plan_sync(db, project_id, goal_text)
    return {"created_nodes": len(nodes)}
