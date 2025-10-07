from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..orchestration import planner

router = APIRouter(prefix="/projects", tags=["plan"])

@router.post("/{project_id}/plan")
def create_plan(project_id: int, payload: dict, db: Session = Depends(get_db)):
    """
    Given a project_id and a plan prompt, auto-generate a branch + plan nodes via AI.
    """
    goal_text = payload.get("prompt")
    if not goal_text:
        raise HTTPException(status_code=400, detail="Missing 'prompt' in body")

    try:
        plan_result = planner.create_plan(db, project_id, goal_text)
        return {"status": "success", "plan": plan_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
