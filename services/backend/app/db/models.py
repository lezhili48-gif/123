from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    source = Column(String, nullable=False)  # wos/scopus
    year_range = Column(String, nullable=True)
    export_format = Column(String, default="ris")
    allowlist = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    status = Column(String, default="SCHEDULED")
    message = Column(Text, default="")
    latest_screenshot = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    needs_download_approval = Column(Boolean, default=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    event = Column(String, nullable=False)
    payload = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    doi = Column(String, nullable=True, index=True)
    title = Column(Text, nullable=False)
    year = Column(Integer, nullable=True)
    journal = Column(String, nullable=True)
    abstract = Column(Text, nullable=True)
    source = Column(String, nullable=True)
    first_author = Column(String, nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow)
    paper_card = Column(JSON, nullable=True)


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    paper_id = Column(Integer, ForeignKey("papers.id"))
    claim = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    magnitude = Column(String, nullable=True)
    mechanism = Column(String, nullable=True)
    source_pointer = Column(String, nullable=False)
    confidence = Column(String, nullable=True)


class Draft(Base):
    __tablename__ = "drafts"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
