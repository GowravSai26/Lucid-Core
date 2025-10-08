# ---------------------------------------------------------
# 🧠 Lucid Reasoning Engine — Gemini 2.5 Pro Integration
# ---------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Backend.app.database import get_db
from Backend.app import models
from Backend.app.config import settings
import google.generativeai as genai

router = APIRouter(prefix="/engine", tags=["Intelligent Engine"])


# ---------------------------------------------------------
# 🔗 Initialize Gemini Client
# ---------------------------------------------------------
genai.configure(api_key=settings.GEMINI_API_KEY)


# ---------------------------------------------------------
# 🧠 Generate a Response for a Prompt and Save as Node
# ---------------------------------------------------------
@router.post("/generate")
async def generate_response(
    project_id: int,
    branch_id: int = None,
    parent_id: int = None,
    prompt: str = None,
    db: Session = Depends(get_db),
):
    """
    Takes user prompt → queries Gemini 2.5 → saves as Node (prompt+response).
    Works like ChatGPT, but all reasoning is versioned in Lucid.
    """

    # ✅ Validate project
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    # ✅ Validate branch if provided
    if branch_id:
        branch = db.query(models.Branch).filter(models.Branch.id == branch_id).first()
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found.")

    # ✅ Create Node placeholder
    node = models.Node(
        project_id=project_id,
        branch_id=branch_id,
        parent_id=parent_id,
        title="Reasoning Step",
        prompt=prompt,
        status=models.NodeStatus.running,
    )
    db.add(node)
    db.commit()
    db.refresh(node)

    try:
        # ---------------------------------------------------------
        # 💬 Call Gemini 2.5 Pro
        # ---------------------------------------------------------
        model = genai.GenerativeModel("gemini-2.0-pro")  # or "gemini-2.5-pro"
        response = model.generate_content(prompt)

        ai_response = response.text.strip() if hasattr(response, "text") else str(response)

        # ✅ Update Node
        node.response_ref = ai_response
        node.status = models.NodeStatus.completed
        db.commit()
        db.refresh(node)

        return {
            "message": "🤖 Gemini reasoning step completed.",
            "node_id": node.id,
            "prompt": prompt,
            "response": ai_response,
        }

    except Exception as e:
        node.status = models.NodeStatus.failed
        db.commit()
        raise HTTPException(status_code=500, detail=f"Gemini generation failed: {str(e)}")
