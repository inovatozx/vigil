from typing import List, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.database import get_db, Session as DBSession, User
from core.auth import get_current_user
from core.exceptions import SessionNotFoundException

router = APIRouter()

class SessionCreate(BaseModel):
    title: str = "Nova Sessão"
    model: Optional[str] = None

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    model: Optional[str] = None
    pinned: Optional[bool] = None
    archived: Optional[bool] = None

@router.get("/sessions", response_model=List[Dict], summary="Listar todas as sessões do usuário")
async def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(DBSession).filter(DBSession.user_id == current_user.id).order_by(DBSession.updated_at.desc()).all()
    return [{
        "id": str(s.id),
        "title": s.title,
        "model": s.model,
        "created_at": s.created_at,
        "updated_at": s.updated_at,
        "pinned": s.pinned,
        "archived": s.archived
    } for s in sessions]

@router.post("/sessions", response_model=Dict, status_code=status.HTTP_201_CREATED, summary="Criar uma nova sessão")
async def create_session(
    request: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_session = DBSession(
        user_id=current_user.id,
        title=request.title,
        model=request.model
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {
        "id": str(new_session.id),
        "title": new_session.title,
        "model": new_session.model,
        "created_at": new_session.created_at,
        "updated_at": new_session.updated_at,
        "pinned": new_session.pinned,
        "archived": new_session.archived
    }

@router.get("/sessions/{session_id}", response_model=Dict, summary="Obter uma sessão específica")
async def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(DBSession).filter(DBSession.id == str(session_id), DBSession.user_id == current_user.id).first()
    if not session:
        raise SessionNotFoundException()
    
    return {
        "id": str(session.id),
        "title": session.title,
        "model": session.model,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "pinned": session.pinned,
        "archived": session.archived
    }

@router.patch("/sessions/{session_id}", response_model=Dict, summary="Atualizar uma sessão")
async def update_session(
    session_id: UUID,
    request: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(DBSession).filter(DBSession.id == str(session_id), DBSession.user_id == current_user.id).first()
    if not session:
        raise SessionNotFoundException()
    
    if request.title is not None:
        session.title = request.title
    if request.model is not None:
        session.model = request.model
    if request.pinned is not None:
        session.pinned = request.pinned
    if request.archived is not None:
        session.archived = request.archived
    
    db.commit()
    db.refresh(session)
    return {
        "id": str(session.id),
        "title": session.title,
        "model": session.model,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "pinned": session.pinned,
        "archived": session.archived
    }

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletar uma sessão")
async def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(DBSession).filter(DBSession.id == str(session_id), DBSession.user_id == current_user.id).first()
    if not session:
        raise SessionNotFoundException()
    
    db.delete(session)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
