from pydantic import BaseModel, Field
from typing import Optional


class ProjectCreate(BaseModel):
    name: str
    query: str
    source: str
    year_range: Optional[str] = None
    export_format: str = "ris"
    allowlist: list[str] = Field(default_factory=list)


class RunStatus(BaseModel):
    id: int
    status: str
    message: str
    latest_screenshot: str | None


class RISIngestRequest(BaseModel):
    project_id: int
    content: str


class DraftGenerateRequest(BaseModel):
    project_id: int
    title: str = "Lit Review Draft"


class EvidenceItem(BaseModel):
    claim: str
    context: str | None = None
    outcome: str | None = None
    magnitude: str | None = None
    mechanism: str | None = None
    source_pointer: str
    confidence: str | None = None
