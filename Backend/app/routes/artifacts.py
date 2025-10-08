# ---------------------------------------------------------
# 📦 Artifact Routes — Upload, List, Retrieve
# ---------------------------------------------------------
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from Backend.app.database import get_db
from Backend.app import models
import boto3
import uuid
import os
from Backend.app.config import settings

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


# ---------------------------------------------------------
# 🔗 Initialize MinIO Client
# ---------------------------------------------------------
s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name="auto",
)


# ---------------------------------------------------------
# 🗂️ Upload an Artifact File for a Node
# ---------------------------------------------------------
@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_artifact(
    node_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Uploads an artifact (file) and associates it with a Node.
    Files are stored in MinIO and path is recorded in DB.
    """

    node = db.query(models.Node).filter(models.Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found.")

    # Generate unique file name
    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    s3_path = f"artifacts/{file_name}"

    try:
        # Upload to MinIO
        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET,
            s3_path,
            ExtraArgs={"ContentType": file.content_type},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Save record in DB
    artifact = models.Artifact(
        node_id=node_id,
        file_path=s3_path,
        file_type=file.content_type,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    return {
        "message": "📦 Artifact uploaded successfully",
        "artifact_id": artifact.id,
        "file_path": s3_path,
        "file_type": file.content_type,
    }


# ---------------------------------------------------------
# 📜 List All Artifacts for a Node
# ---------------------------------------------------------
@router.get("/node/{node_id}")
def list_artifacts(node_id: int, db: Session = Depends(get_db)):
    artifacts = db.query(models.Artifact).filter(models.Artifact.node_id == node_id).all()
    if not artifacts:
        raise HTTPException(status_code=404, detail="No artifacts found for this node.")

    return {
        "node_id": node_id,
        "artifacts": [
            {"id": a.id, "file_path": a.file_path, "file_type": a.file_type, "created_at": a.created_at}
            for a in artifacts
        ],
    }


# ---------------------------------------------------------
# 🔍 Get Artifact Metadata by ID
# ---------------------------------------------------------
@router.get("/{artifact_id}")
def get_artifact(artifact_id: int, db: Session = Depends(get_db)):
    artifact = db.query(models.Artifact).filter(models.Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found.")

    return {
        "id": artifact.id,
        "file_path": artifact.file_path,
        "file_type": artifact.file_type,
        "created_at": artifact.created_at,
        "node_id": artifact.node_id,
    }
