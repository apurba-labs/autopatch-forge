from pydantic import BaseModel, Field
from typing import Dict, Any

class PipelinePayload(BaseModel):
    repo_url: str
    branch: str
    commit_sha: str
    error_log: str

class AgentAnalysis(BaseModel):
    exception_type: str
    target_file: str
    line_number: int
    raw_error: str

class AgentValidation(BaseModel):
    confidence: float = Field(..., description="Multi-agent reliability score between 0.0 and 1.0")
    risk: str = Field(..., description="Risk assessment: low, medium, high")
    recommended_action: str
    reasoning: str