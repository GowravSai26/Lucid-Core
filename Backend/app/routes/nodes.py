from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..orchestration import executor

router = APIRouter(prefix="/nodes", tags=["nodes"])

@router.post("/", response_model=schemas.NodeRead)
def create_node(payload: schemas.NodeCreate, db: Session = Depends(get_db)):
    # create node in default main branch of project (quick helper)
    # client should normally call /projects/{id}/plan or create nodes explicitly
    # require project_id and branch_id in production
    raise HTTPException(status_code=400, detail="Use project plan endpoint or provide branch_id/project_id")

@router.post("/{node_id}/run")
def run_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    result = executor.run_node_sync(db, node_id)
    return result
