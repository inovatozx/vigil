from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.database import get_db, User, ProviderConfig
from core.auth import get_current_user
from core.exceptions import ProviderConfigNotFoundException
from src.llm_core import llm_core
from src.model_discovery import ModelDiscovery

router = APIRouter()
model_discovery = ModelDiscovery()

class ProviderConfigCreate(BaseModel):
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: bool = True

class ProviderConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/models", response_model=List[Dict], summary="Listar todos os modelos LLM disponíveis de provedores configurados")
async def list_available_models(
    current_user: User = Depends(get_current_user)
):
    # This will discover models from all configured providers
    # In a real scenario, this would involve checking user's ProviderConfig in DB
    # For now, it discovers from default Ollama and OpenAI (if API key is set in env)
    return await model_discovery.discover_all_models()

@router.get("/models/providers", response_model=List[Dict], summary="Listar configurações de provedores LLM do usuário")
async def list_provider_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    configs = db.query(ProviderConfig).filter(ProviderConfig.user_id == current_user.id).all()
    return [{
        "id": c.id,
        "provider": c.provider,
        "base_url": c.base_url,
        "is_active": c.is_active,
        "created_at": c.created_at
    } for c in configs]

@router.post("/models/providers", response_model=Dict, status_code=status.HTTP_201_CREATED, summary="Adicionar ou atualizar configuração de provedor LLM")
async def create_or_update_provider_config(
    request: ProviderConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # In a real app, api_key would be encrypted before saving
    existing_config = db.query(ProviderConfig).filter(
        ProviderConfig.user_id == current_user.id,
        ProviderConfig.provider == request.provider
    ).first()

    if existing_config:
        if request.api_key is not None:
            existing_config.api_key_encrypted = request.api_key # Placeholder for encryption
        if request.base_url is not None:
            existing_config.base_url = request.base_url
        if request.is_active is not None:
            existing_config.is_active = request.is_active
        db.commit()
        db.refresh(existing_config)
        return {"message": "Provider config updated", "id": existing_config.id}
    else:
        new_config = ProviderConfig(
            user_id=current_user.id,
            provider=request.provider,
            api_key_encrypted=request.api_key, # Placeholder for encryption
            base_url=request.base_url,
            is_active=request.is_active
        )
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        return {"message": "Provider config created", "id": new_config.id}

@router.delete("/models/providers/{config_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deletar configuração de provedor LLM")
async def delete_provider_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = db.query(ProviderConfig).filter(ProviderConfig.id == config_id, ProviderConfig.user_id == current_user.id).first()
    if not config:
        raise ProviderConfigNotFoundException()
    db.delete(config)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Placeholder for model pull/remove/status routes (e.g., for Ollama)
# @router.post("/models/pull", summary="Baixar um modelo (Ollama)")
# async def pull_model(model_name: str, current_user: User = Depends(get_current_user)):
#     # Logic to interact with Ollama API to pull a model
#     return {"message": f"Attempting to pull model {model_name}"}
