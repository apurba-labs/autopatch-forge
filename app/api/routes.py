import os
import time

from fastapi import APIRouter, HTTPException

from app.agents.analyzer import analyze_log_payload
from app.agents.patch_generator import generate_patch
from app.agents.risk_assessor import evaluate_patch_risk
from app.core.config import logger
from app.models.schemas import PipelinePayload
from app.services.github import create_automated_pull_request
from app.services.patch import apply_local_patch

router = APIRouter(prefix="/api/v1", tags=["Pipeline"])


@router.post("/intercept")
async def intercept_pipeline_failure(payload: PipelinePayload):
    """
    AutoPatch Forge Pipeline

    Flow

    1. Trace Analyzer Agent
    2. Patch Planning Agent
    3. AI Risk Assessment Agent (Gemma)
    4. Deterministic Patch Engine
    5. GitHub Automation Service
    """

    started = time.perf_counter()

    logger.info(
        "[PIPELINE] Processing commit %s (%s)",
        payload.commit_sha,
        payload.branch,
    )

    stages = ["received"]

    try:

        # ==========================================================
        # Stage 1 - Trace Analysis
        # ==========================================================
        analysis_started = time.perf_counter()

        analysis = await analyze_log_payload(payload.error_log)

        analysis_ms = round(
            (time.perf_counter() - analysis_started) * 1000,
            2,
        )

        stages.append("analyzed")

        # ==========================================================
        # Stage 2 - Patch Planning
        # ==========================================================
        patch_started = time.perf_counter()

        proposed_patch = await generate_patch(analysis)

        patch_generation_ms = round(
            (time.perf_counter() - patch_started) * 1000,
            2,
        )

        stages.append("patch_generated")

        # ==========================================================
        # Manual Review
        # ==========================================================
        if proposed_patch.get("operation") == "manual_review":

            total_ms = round(
                (time.perf_counter() - started) * 1000,
                2,
            )

            return {
                "incident_id": payload.commit_sha,
                "engine_state": "manual_review_required",
                "pipeline": stages,
                "assessment": {
                    "confidence": 0.0,
                    "risk": "high",
                },
                "estimated_fix_time": f"{total_ms} ms",
                "metrics": {
                    "analysis_ms": analysis_ms,
                    "patch_generation_ms": patch_generation_ms,
                    "total_ms": total_ms,
                },
                "telemetry": {
                    "analysis": analysis,
                    "patch": proposed_patch,
                    "validation": {
                        "recommended_action": "Manual Review",
                        "reasoning": proposed_patch.get(
                            "reason",
                            "No remediation strategy available.",
                        ),
                    },
                    "patch_applied": False,
                    "pr_created": False,
                },
            }
        # ==========================================================
        # Stage 3 - AI Risk Assessment
        # ==========================================================
        risk_started = time.perf_counter()

        validation = await evaluate_patch_risk(
            analysis,
            proposed_patch["content"],
        )

        risk_assessment_ms = round(
            (time.perf_counter() - risk_started) * 1000,
            2,
        )

        stages.append("ai_validation_complete")

        target_file = analysis.get("target_file", "unknown")
        line_number = analysis.get("line_number", 1)

        patch_applied = False
        pr_created = False

        # ==========================================================
        # Stage 4 - Deterministic Patch Engine
        # ==========================================================
        patch_started = time.perf_counter()

        if validation.get("risk") == "low":

            if (
                target_file != "unknown"
                and "helpers.py" in target_file
            ):
                directory = os.path.dirname(target_file)

                if directory:
                    os.makedirs(directory, exist_ok=True)

                if not os.path.exists(target_file):
                    with open(target_file, "w") as f:
                        f.write(
                            "# AutoPatch mock asset\n"
                            "def parse():\n"
                            "    pass\n"
                        )

            patch_applied = apply_local_patch(
                target_file=target_file,
                line_number=line_number,
                proposed_patch=proposed_patch["content"],
            )

            if patch_applied:
                stages.append("patched")

        patch_execution_ms = round(
            (time.perf_counter() - patch_started) * 1000,
            2,
        )

        # ==========================================================
        # Stage 5 - GitHub Automation
        # ==========================================================
        git_started = time.perf_counter()

        if patch_applied:

            pr_created = create_automated_pull_request(
                repo_url=payload.repo_url,
                branch=payload.branch,
                commit_sha=payload.commit_sha,
                target_file=target_file,
            )

            if pr_created:
                stages.append("pull_request_created")

        git_automation_ms = round(
            (time.perf_counter() - git_started) * 1000,
            2,
        )

        total_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        logger.info(
            "[PIPELINE] Completed successfully in %.2f ms",
            total_ms,
        )

        return {
            "incident_id": payload.commit_sha,
            "engine_state": (
                "cloud_pr_dispatched"
                if pr_created
                else (
                    "patched_locally"
                    if patch_applied
                    else "analysis_complete"
                )
            ),
            "pipeline": stages,
            "assessment": {
                "confidence": validation.get("confidence", 0.0),
                "risk": validation.get("risk", "unknown"),
            },
            "estimated_fix_time": f"{total_ms} ms",
            "metrics": {
                "analysis_ms": analysis_ms,
                "patch_generation_ms": patch_generation_ms,
                "risk_assessment_ms": risk_assessment_ms,
                "patch_execution_ms": patch_execution_ms,
                "git_automation_ms": git_automation_ms,
                "total_ms": total_ms,
            },
            "telemetry": {
                "analysis": analysis,
                "patch": proposed_patch,
                "validation": {
                    "recommended_action": validation.get(
                        "recommended_action"
                    ),
                    "reasoning": validation.get(
                        "reasoning"
                    ),
                },
                "patch_applied": patch_applied,
                "pr_created": pr_created,
            },
        }

    except Exception:

        logger.exception(
            "[PIPELINE] Fatal orchestration failure"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "message": "Pipeline orchestration failed.",
                "reason": "Internal orchestration error.",
            },
        )