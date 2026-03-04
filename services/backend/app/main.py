from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import threading

from app.db.database import Base, engine, get_db
from app.db.models import Project, Run, Paper, Evidence, Draft
from app.schemas.schemas import ProjectCreate, RunStatus, RISIngestRequest, DraftGenerateRequest
from app.services.allowlist import host_allowed
from app.services.ris_parser import parse_ris
from app.services.dedup import is_duplicate
from app.services.evidence import extract_evidence_from_abstract
from app.services.docx_export import generate_docx
from app.workflow.orchestrator import run_workflow
from app.core.config import get_settings
from app.services.scheduler import scheduler, start_scheduler

app = FastAPI(title="LitReviewAgent Backend")
state_events: dict[int, threading.Event] = {}


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    start_scheduler()


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/projects")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    p = Project(
        name=payload.name,
        query=payload.query,
        source=payload.source,
        year_range=payload.year_range,
        export_format=payload.export_format,
        allowlist=",".join(payload.allowlist),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@app.get("/api/projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.id.desc()).all()


@app.post("/api/runs/{project_id}/start")
def start_run(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    r = Run(project_id=project.id, status="SCHEDULED", message="Queued")
    db.add(r)
    db.commit()
    db.refresh(r)
    event = threading.Event()
    event.set()
    state_events[r.id] = event

    def update(status: str, message: str, screenshot: str | None):
        local = next(get_db())
        rr = local.query(Run).filter(Run.id == r.id).first()
        rr.status = status
        rr.message = message
        rr.latest_screenshot = screenshot
        rr.updated_at = datetime.utcnow()
        local.commit()
        local.close()

    def wait_approve():
        event.clear()
        event.wait()

    thread = threading.Thread(
        target=run_workflow,
        args=(
            {
                "id": project.id,
                "source": project.source,
                "query": project.query,
                "year_range": project.year_range,
                "allowlist": project.allowlist.split(",") if project.allowlist else get_settings().allowlist,
            },
            r.id,
            update,
            wait_approve,
        ),
        daemon=True,
    )
    thread.start()
    return {"run_id": r.id}


@app.post("/api/runs/{run_id}/approve_takeover")
def approve_takeover(run_id: int):
    event = state_events.get(run_id)
    if not event:
        raise HTTPException(404, "Run not found")
    event.set()
    return {"ok": True}


@app.get("/api/runs/{run_id}/status", response_model=RunStatus)
def run_status(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(404, "Run not found")
    return RunStatus(id=run.id, status=run.status, message=run.message, latest_screenshot=run.latest_screenshot)


@app.get("/api/runs/{run_id}/latest_screenshot")
def latest_screenshot(run_id: int, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run or not run.latest_screenshot:
        raise HTTPException(404, "Screenshot not found")
    return FileResponse(run.latest_screenshot, media_type="image/png")


@app.post("/api/ingest/ris")
def ingest_ris(payload: RISIngestRequest, db: Session = Depends(get_db)):
    records = parse_ris(payload.content)
    existing = [
        {"doi": p.doi, "title": p.title, "year": p.year, "first_author": p.first_author}
        for p in db.query(Paper).filter(Paper.project_id == payload.project_id).all()
    ]
    inserted = 0
    skipped = 0
    for rec in records:
        candidate = {
            "doi": rec.get("doi"),
            "title": rec.get("title", ""),
            "year": rec.get("year"),
            "first_author": (rec.get("authors") or [""])[0],
        }
        if is_duplicate(candidate, existing):
            skipped += 1
            continue
        paper = Paper(
            project_id=payload.project_id,
            doi=rec.get("doi"),
            title=rec.get("title", "Untitled"),
            year=int(rec.get("year")) if str(rec.get("year", "")).isdigit() else None,
            journal=rec.get("journal"),
            abstract=rec.get("abstract"),
            source="ris",
            first_author=(rec.get("authors") or [None])[0],
            paper_card={"summary": (rec.get("abstract") or "")[:240]},
        )
        db.add(paper)
        db.flush()
        evs = extract_evidence_from_abstract(paper.doi, paper.abstract)
        for e in evs:
            db.add(Evidence(project_id=payload.project_id, paper_id=paper.id, **e))
        inserted += 1
        existing.append(candidate)
    db.commit()
    return {"inserted": inserted, "skipped": skipped}


@app.post("/api/drafts/generate")
def drafts_generate(payload: DraftGenerateRequest, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    papers = db.query(Paper).filter(Paper.project_id == payload.project_id).all()
    evidence = db.query(Evidence).filter(Evidence.project_id == payload.project_id).all()
    p_data = [{"doi": p.doi, "year": p.year, "journal": p.journal, "abstract": p.abstract} for p in papers]
    e_data = [{"mechanism": e.mechanism, "outcome": e.outcome, "claim": e.claim, "source_pointer": e.source_pointer} for e in evidence]
    path = generate_docx(project.name, p_data, e_data, get_settings().data_dir / "drafts", payload.title)
    d = Draft(project_id=payload.project_id, file_path=str(path))
    db.add(d)
    db.commit()
    return {"path": str(path)}


@app.get("/api/files/{file_path:path}")
def get_file(file_path: str):
    settings = get_settings()
    target = (Path(file_path)).resolve()
    if settings.data_dir.resolve() not in target.parents and target != settings.data_dir.resolve():
        raise HTTPException(403, "Path blocked")
    if not target.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(target)


@app.get("/api/papers/{project_id}")
def list_papers(project_id: int, db: Session = Depends(get_db)):
    return db.query(Paper).filter(Paper.project_id == project_id).all()


@app.get("/api/evidence/{project_id}")
def list_evidence(project_id: int, db: Session = Depends(get_db)):
    return db.query(Evidence).filter(Evidence.project_id == project_id).all()


@app.get("/api/drafts/{project_id}")
def list_drafts(project_id: int, db: Session = Depends(get_db)):
    return db.query(Draft).filter(Draft.project_id == project_id).all()
