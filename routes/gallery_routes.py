from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from src.tool_implementations import generate_image

router = APIRouter()

class ImageGenerateRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"
    n: int = 1

class GalleryItemCreate(BaseModel):
    image_url: str
    prompt: str
    tags: Optional[List[str]] = None

class GalleryItemResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
    prompt: str
    tags: Optional[List[str]] = None
    created_at: str

# In-memory store for gallery items (replace with DB in real app)
gallery_db: Dict[str, Dict[str, Any]] = {}

# Placeholder for user dependency
async def get_current_user():
    return {"id": "test_user", "username": "testuser"}

@router.post("/gallery/generate", response_model=List[GalleryItemResponse])
async def generate_gallery_image(request: ImageGenerateRequest, current_user: dict = Depends(get_current_user)):
    print(f"Generating image for user {current_user["id"]} with prompt: {request.prompt}")
    try:
        image_urls = await generate_image(request.prompt, request.size, request.quality, request.n)
        gallery_items = []
        for url in image_urls:
            item_id = str(uuid4())
            new_item = {
                "id": item_id,
                "user_id": current_user["id"],
                "image_url": url,
                "prompt": request.prompt,
                "tags": ["generated"],
                "created_at": datetime.now().isoformat(),
            }
            gallery_db[item_id] = new_item
            gallery_items.append(new_item)
        return gallery_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@router.post("/gallery", response_model=GalleryItemResponse)
async def add_gallery_item(item: GalleryItemCreate, current_user: dict = Depends(get_current_user)):
    item_id = str(uuid4())
    new_item = {
        "id": item_id,
        "user_id": current_user["id"],
        "image_url": item.image_url,
        "prompt": item.prompt,
        "tags": item.tags,
        "created_at": datetime.now().isoformat(),
    }
    gallery_db[item_id] = new_item
    return new_item

@router.get("/gallery", response_model=List[GalleryItemResponse])
async def list_gallery_items(current_user: dict = Depends(get_current_user)):
    return [item for item in gallery_db.values() if item["user_id"] == current_user["id"]]

@router.get("/gallery/{item_id}", response_model=GalleryItemResponse)
async def get_gallery_item(item_id: str, current_user: dict = Depends(get_current_user)):
    item = gallery_db.get(item_id)
    if not item or item["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Gallery item not found")
    return item

@router.delete("/gallery/{item_id}", status_code=204)
async def delete_gallery_item(item_id: str, current_user: dict = Depends(get_current_user)):
    item = gallery_db.get(item_id)
    if not item or item["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Gallery item not found")
    del gallery_db[item_id]
    return
