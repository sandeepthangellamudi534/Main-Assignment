import pymongo
Client = pymongo.MongoClient("mongodb://localhost:27017/")
tdb = Client["test"]
from fastapi import FastAPI
import nest_asyncio
import uvicorn
from pymongo import MongoClient
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')  # Replace with your MongoDB URI if needed
db = client['your_database_name']  # Create database
items_collection = db['items']  # Create Items collection
clock_in_collection = db['clock_in_records']  # Create Clock-In collection

nest_asyncio.apply()
app = FastAPI()

class Item(BaseModel):
    name: str
    email: EmailStr
    item_name: str
    quantity: int
    expiry_date: datetime

class ClockInRecord(BaseModel):
    email: EmailStr
    location: str

def create_item(item_data):
    item_data['insert_date'] = datetime.now()  # Use datetime for insert_date
    items_collection.insert_one(item_data)

def get_item_by_id(item_id):
    return items_collection.find_one({"_id": ObjectId(item_id)})

def update_item(item_id, updated_data):
    items_collection.update_one({"_id": ObjectId(item_id)}, {"$set": updated_data})

def delete_item(item_id):
    items_collection.delete_one({"_id": ObjectId(item_id)})

def create_clock_in(clock_in_data):
    clock_in_data['insert_date'] = datetime.now()
    clock_in_collection.insert_one(clock_in_data)

def get_clock_in_by_id(clock_in_id):
    return clock_in_collection.find_one({"_id": ObjectId(clock_in_id)})

def update_clock_in(clock_in_id, updated_data):
    clock_in_collection.update_one({"_id": ObjectId(clock_in_id)}, {"$set": updated_data})

def delete_clock_in(clock_in_id):
    clock_in_collection.delete_one({"_id": ObjectId(clock_in_id)})

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI CRUD Application"}

@app.post("/items/")
def create_new_item(item: Item):
    create_item(item.dict())
    return {"message": "Item created successfully"}

@app.get("/items/{item_id}")
def get_item(item_id):
    return get_item_by_id(item_id)

@app.put("/items/{item_id}")
def update_item_by_id(item_id: str, item: Item):
    update_item(item_id, item.dict())
    return {"message": "Item updated"}

@app.delete("/items/{item_id}")
def delete_item_by_id(item_id: str):
    delete_item(item_id)
    return {"message": "Item deleted"}

@app.post("/clock-in/")
def create_clock_in_entry(clock_in: ClockInRecord):
    create_clock_in(clock_in.dict())
    return {"message": "Clock-in record created"}

@app.get("/clock-in/{clock_in_id}")
def get_clock_in(clock_in_id: str):
    return get_clock_in_by_id(clock_in_id)

@app.put("/clock-in/{clock_in_id}")
def update_clock_in_by_id(clock_in_id: str, clock_in: ClockInRecord):
    update_clock_in(clock_in_id, clock_in.dict())
    return {"message": "Clock-in record updated"}

@app.delete("/clock-in/{clock_in_id}")
def delete_clock_in_by_id(clock_in_id: str):
    delete_clock_in(clock_in_id)
    return {"message": "Clock-in record deleted"}


@app.get("/items/filter/")
def filter_items(email: str = None, expiry_date: datetime = None,
                 quantity: int = None):  # Change expiry_date to datetime
    query = {}
    if email:
        query["email"] = email
    if expiry_date:
        query["expiry_date"] = {"$gt": expiry_date}
    if quantity:
        query["quantity"] = {"$gte": quantity}

    return list(items_collection.find(query))

@app.get("/items/aggregate/")
def aggregate_items_by_email():
    pipeline = [
        {"$group": {"_id": "$email", "count": {"$sum": 1}}}
    ]
    return list(items_collection.aggregate(pipeline))


@app.get("/clock-in/filter/")
def filter_clock_in(email: str = None, location: str = None, insert_date: datetime = None):
    query = {}
    if email:
        query["email"] = email
    if location:
        query["location"] = location
    if insert_date:
        query["insert_date"] = {"$gt": insert_date}

    return list(clock_in_collection.find(query))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

