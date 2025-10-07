import json
from sqlalchemy.orm import Session
from Backend.app import models
from Backend.utils.llm_router import call_chat_completion

def generate_plan_outline(prompt: str):
    """
    Uses LLM (Gemini/OpenAI) to generate a structured plan outline.
    Returns a list of task steps.
    """
    system_prompt = (
        "You are a senior AI software architect. "
        "Given a user goal, decompose it into clear technical steps required to achieve it. "
        "Respond in JSON format like this:\n"
        "{ 'steps': [ {'title': '...', 'description': '...'}, ... ] }"
    )

    response = call_chat_completion(prompt=prompt, system=system_prompt)
    text = response.get("text", "").strip()

    # Try to extract valid JSON (LLMs sometimes add markdown formatting)
    try:
        text = text.replace("```json", "").replace("```", "")
        data = json.loads(text)
        return data.get("steps", [])
    except Exception:
        print("⚠️ LLM returned non-JSON, fallback to single node.")
        return [{"title": "Initial Plan", "description": text[:500]}]


def create_plan(db: Session, project_id: int, plan_prompt: str):
    """
    1️⃣ Generate a task plan using LLM.
    2️⃣ Store plan and nodes in DB.
    """
    # Step 1: Get project
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise ValueError(f"Project ID {project_id} not found.")

    # Step 2: Create branch for this plan
    branch = models.Branch(project_id=project_id, name="ai-plan", status="draft")
    db.add(branch)
    db.commit()
    db.refresh(branch)

    # Step 3: Generate plan via Gemini/OpenAI
    steps = generate_plan_outline(plan_prompt)

    # Step 4: Store nodes
    nodes = []
    for idx, step in enumerate(steps):
        node = models.Node(
            project_id=project_id,
            branch_id=branch.id,
            parent_id=None if idx == 0 else nodes[-1].id,
            title=step.get("title", f"Step {idx+1}"),
            prompt=step.get("description", ""),
        )
        db.add(node)
        db.flush()
        nodes.append(node)

    # Step 5: Commit to DB
    db.commit()

    return {
        "branch_id": branch.id,
        "total_nodes": len(nodes),
        "nodes": [{"id": n.id, "title": n.title} for n in nodes],
    }
