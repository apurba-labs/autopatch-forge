from fastapi import APIRouter
import time
import os
from app.models.schemas import PipelinePayload
from app.agents.analyzer import analyze_log_payload
from app.agents.validator import validate_patch_safety
from app.services.patch import apply_local_patch
from app.services.github import create_automated_pull_request
from app.core.config import logger

router = APIRouter(prefix="/api/v1")

@router.post("/intercept")
async def intercept_pipeline_failure(payload: PipelinePayload):
    start_time = time.time()
    logger.info(f"[ROUTE] Intercepting pipeline crash for commit {payload.commit_sha}")
    
    # 1. Run multi-agent decoding matrix
    analysis = await analyze_log_payload(payload.error_log)
    proposed_patch = "import httpx"  
    validation = await validate_patch_safety(analysis, proposed_patch)
    
    target_file = analysis.get("target_file") or "app/utils/helpers.py"
    patch_applied = False
    pr_created = False
    
    # 2. Execute patch if the risk is verified as low
    if validation.get("risk") == "low":
        if "helpers.py" in target_file:
            os.makedirs("app/utils", exist_ok=True)
            if not os.path.exists(target_file):
                with open(target_file, "w") as f:
                    f.write("# Mock broken code asset\ndef parse():\n    pass\n")
        
        patch_applied = apply_local_patch(
            target_file=target_file,
            line_number=analysis.get("line_number", 1),
            proposed_patch=proposed_patch
        )
        
        # 3. NEW: If patched locally, trigger automated git branch automation tracking
        if patch_applied:
            pr_created = create_automated_pull_request(
                repo_url=payload.repo_url,
                branch=payload.branch,
                commit_sha=payload.commit_sha,
                target_file=target_file
            )

    execution_time = f"{round(time.time() - start_time, 2)}s"
    return {
        "incident_id": payload.commit_sha,
        "engine_state": "cloud_pr_dispatched" if pr_created else ("patched_locally" if patch_applied else "failed_execution"),
        "confidence": validation.get("confidence"),
        "estimated_fix_time": execution_time,
        "telemetry": {
            "analysis": analysis,
            "patch": proposed_patch,
            "validation": validation,
            "patch_applied": patch_applied,
            "pr_created": pr_created
        }
    }