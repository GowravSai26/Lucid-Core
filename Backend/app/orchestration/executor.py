from Backend.app.database import SessionLocal
from Backend.app import models
from Backend.utils.llm_router import call_chat_completion
import datetime, os

def execute_node(node_id: int):
    """
    Executes a node’s LLM prompt using Gemini/OpenAI.
    Now fully Redis-safe — creates its own DB session inside worker.
    """
    print(f"🧠 Executing Node {node_id}...")

    db = SessionLocal()  # Create new DB session in worker
    try:
        node = db.query(models.Node).filter(models.Node.id == node_id).first()
        if not node:
            print(f"❌ Node {node_id} not found in DB.")
            return {"error": "Node not found"}

        print(f"🔍 Prompt: {node.prompt[:80]}")

        # Call LLM (Gemini > OpenAI)
        result = call_chat_completion(node.prompt or "")
        output = result.get("text", "[Empty response]")

        # Save LLM output
        node.status = models.NodeStatus.ok
        node.response_ref = f"node_{node.id}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"

        artifacts_path = os.path.join("artifacts", node.response_ref)
        os.makedirs("artifacts", exist_ok=True)
        with open(artifacts_path, "w", encoding="utf-8") as f:
            f.write(output)

        db.commit()
        print(f"✅ Node {node_id} executed successfully.")
        return {
            "node_id": node.id,
            "prompt": node.prompt,
            "output": output[:500],
            "artifact_path": os.path.abspath(artifacts_path)
        }

    except Exception as e:
        print(f"❌ Execution error for node {node_id}: {e}")
        db.rollback()
        return {"error": str(e)}

    finally:
        db.close()
