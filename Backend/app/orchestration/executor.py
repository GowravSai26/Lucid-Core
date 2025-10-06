from Backend.utils.llm_router import call_chat_completion
from Backend.utils.storage import upload_text
from .. import models
from sqlalchemy.orm import Session

def build_context(db: Session, node: models.Node):
    # For MVP: use parent prompt/summary only
    ctx = ""
    if node.parent_id:
        parent = db.query(models.Node).filter(models.Node.id == node.parent_id).first()
        if parent and parent.prompt:
            ctx += f"Parent prompt: {parent.prompt}\nParent response: see parent node\n\n"
    ctx += f"Current prompt: {node.prompt}\n"
    return ctx

def run_node_sync(db: Session, node_id: int):
    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        return {"error": "node not found"}

    # build prompt/context
    context = build_context(db, node)
    try:
        resp = call_chat_completion(prompt=context, system="You are a developer assistant.", temperature=0.0)
        text = resp.get("text", "")
        # store text to S3 via storage helper
        key = upload_text(f"node_{node.id}_response.txt", text)
        node.response_ref = key
        node.status = models.NodeStatus.ok
        db.add(node)
        db.commit()
        return {"node_id": node.id, "response_ref": key}
    except Exception as e:
        node.status = models.NodeStatus.error
        db.add(node)
        db.commit()
        return {"node_id": node.id, "error": str(e)}
