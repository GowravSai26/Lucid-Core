from Backend.utils.llm_router import call_chat_completion
from ..import models
from sqlalchemy.orm import Session
import re

def parse_numbered_steps(text: str):
    # simple parser: lines starting with "1." or "1)"
    steps = []
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r'^\s*(\d+)[\.\)]\s*(.+)$', line)
        if m:
            steps.append(m.group(2).strip())
    # fallback: split by double newline if none found
    if not steps:
        parts = [p.strip() for p in text.split("\n\n") if p.strip()]
        steps = parts
    return steps

def generate_plan_sync(db: Session, project_id: int, goal_text: str):
    """
    Synchronous planner: calls LLM and writes nodes into DB under main branch.
    """
    # Compose prompt
    prompt = f"Break the goal into a numbered sequence of discrete steps. Goal:\n{goal_text}\n\nReturn only numbered steps."

    resp = call_chat_completion(prompt=prompt, system="You are a concise planner.", temperature=0.0)
    text = resp.get("text", "") or ""
    steps = parse_numbered_steps(text)

    # find main branch
    branch = db.query(models.Branch).filter(models.Branch.project_id == project_id).order_by(models.Branch.id).first()
    if not branch:
        # create main branch if missing
        branch = models.Branch(project_id=project_id, name="main")
        db.add(branch)
        db.commit()
        db.refresh(branch)

    created_nodes = []
    prev_node = None
    for i, s in enumerate(steps, start=1):
        node = models.Node(project_id=project_id, branch_id=branch.id, parent_id=prev_node.id if prev_node else None,
                           title=f"Step {i}: {s[:80]}", prompt=s)
        db.add(node)
        db.commit()
        db.refresh(node)
        prev_node = node
        created_nodes.append(node)
    return created_nodes
