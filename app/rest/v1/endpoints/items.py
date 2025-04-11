from app.models.item import Item, ItemCreate
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

# In-memory "database"
fake_items_db = []

@router.get("", response_model=List[Item])
async def read_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@router.post("", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    item_dict = item.dict()
    fake_items_db.append(item_dict)
    return item_dict

@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    if item_id >= len(fake_items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_items_db[item_id]