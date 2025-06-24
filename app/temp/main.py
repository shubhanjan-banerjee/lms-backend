from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Sample in-memory storage
data_store = {}

class Item(BaseModel):
    id: int
    name: str
    value: str

@app.post("/items/")
def create_item(item: Item):
    if item.id in data_store:
        raise HTTPException(status_code=400, detail="Item already exists")
    data_store[item.id] = item
    return {"message": "Item created", "item": item}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    item = data_store.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Rename: main.py moved to app/main.py as part of MVC structure refactor. Resource is now employees.
