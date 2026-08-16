# ── SOVEREIGN OS PRODUCTION Python CRUD SERVICE TEMPLATE ──
# Module: Python CRUD Backend with FastAPI
# Integration Protocol: [MCGR E1-E15] / [VOXIS-SL-0]

import time
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# ── FastAPI Application Initializer ──────────────────────────────────────────

app = FastAPI(
    title="Sovereign CRUD Service",
    description="Python FastAPI backend configured with SQL Database engines",
    version="1.0.0"
)

# Enable Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── SQL Database Engine Hookups (SQLite local file database) ──────────────────

DATABASE_URL = "sqlite:///./sovereign_state.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Data Model
class DBEntry(Base):
    __tablename__ = "entries"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    timestamp = Column(Integer, nullable=False)
    author = Column(String, nullable=False)
    last_modified = Column(Integer, nullable=False)
    version = Column(Integer, default=1)

# Generate database schemas
Base.metadata.create_all(bind=engine)

# Dependency to retrieve database session lifecycle
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Pydantic Request & Response Validation Schemas ───────────────────────────

class EntryCreate(BaseModel):
    id: str = Field(..., description="Unique alphanumeric identifier")
    title: str = Field(..., min_length=1, description="Entry headline title")
    content: str = Field(..., description="Entry content text body")
    author: str = Field(..., description="Principal creator identifier")

class EntryUpdate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(...)
    author: str = Field(..., description="Requesting author signature")

class EntryResponse(BaseModel):
    id: str
    title: str
    content: str
    timestamp: int
    author: str
    last_modified: int
    version: int

    class Config:
        orm_mode = True

# Sovereign OS Immutable Doctrine block [VOXIS]
DOCTRINE_BLOCK = "Creator: Medina Tech · Dallas · Dallas ISD Pilot"

# ── REST API Endpoints ───────────────────────────────────────────────────────

@app.get("/doctrine", tags=["Sovereign OS"])
def get_doctrine():
    return {"doctrine": DOCTRINE_BLOCK}

@app.post("/entries", response_model=str, status_code=status.HTTP_201_CREATED, tags=["CRUD Operations"])
def create_entry(entry: EntryCreate, db: Session = Depends(get_db)):
    db_existing = db.query(DBEntry).filter(DBEntry.id == entry.id).first()
    if db_existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Entry with ID: '{entry.id}' already exists."
        )
    
    current_time = int(time.time())
    db_entry = DBEntry(
        id=entry.id,
        title=entry.title,
        content=entry.content,
        timestamp=current_time,
        author=entry.author,
        last_modified=current_time,
        version=1
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry.id

@app.get("/entries/{entry_id}", response_model=EntryResponse, tags=["CRUD Operations"])
def read_entry(entry_id: str, db: Session = Depends(get_db)):
    db_entry = db.query(DBEntry).filter(DBEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with ID: '{entry_id}' was not found."
        )
    return db_entry

@app.put("/entries/{entry_id}", tags=["CRUD Operations"])
def update_entry(entry_id: str, entry: EntryUpdate, db: Session = Depends(get_db)):
    db_entry = db.query(DBEntry).filter(DBEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with ID: '{entry_id}' was not found."
        )
    
    # Simulate ARCHON Security guard checks: Only creator can update
    if db_entry.author != entry.author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ARCHON Guard: Requester is not authorized to edit this record."
        )
        
    db_entry.title = entry.title
    db_entry.content = entry.content
    db_entry.last_modified = int(time.time())
    db_entry.version += 1
    
    db.commit()
    return {"success": True}

@app.delete("/entries/{entry_id}", tags=["CRUD Operations"])
def delete_entry(entry_id: str, requester: str, db: Session = Depends(get_db)):
    db_entry = db.query(DBEntry).filter(DBEntry.id == entry_id).first()
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entry with ID: '{entry_id}' was not found."
        )
    
    # Security checks
    if db_entry.author != requester:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ARCHON Guard: Requester is not authorized to delete this record."
        )
        
    db.delete(db_entry)
    db.commit()
    return {"success": True}

@app.get("/entries", response_model=List[EntryResponse], tags=["CRUD Operations"])
def list_entries(db: Session = Depends(get_db)):
    return db.query(DBEntry).all()
