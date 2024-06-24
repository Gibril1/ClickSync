from mongodb import get_database
from fastapi import HTTPException
import logging
from datetime import datetime, timedelta


class MongoDBCRUDService:
    def __init__(self, model):
        self.model = model

    async def create_item(self, item: dict):
        try:
            db = await get_database()
            result = await db[self.model].insert_one(item)
            item_id = result.inserted_id
            # Convert the ObjectId to a string
            item_id_str = str(item_id)
            saved_item = await db[self.model].find_one({"_id": item_id}, {"_id": 0})
            return {**saved_item, "id": item_id_str}  # Include the item_id as a string
        except Exception as e:
            logging.error(f"Error creating item: {str(e)}")
            raise HTTPException(status_code=500, detail="Error creating item")

    async def create_or_update_item(self, key_name: str, key_value, item: dict):
        try:
            db = await get_database()

            # Check if the item already exists
            existing_item = await db[self.model].find_one({key_name: key_value})

            if existing_item:
                # Update the existing item
                result = await db[self.model].update_one(
                    {key_name: key_value}, {"$set": item}
                )
                updated_item = await db[self.model].find_one({key_name: key_value})
                return updated_item
            else:
                # Create a new item
                result = await db[self.model].insert_one(item)
                item_id = result.inserted_id
                item_id_str = str(item_id)
                saved_item = await db[self.model].find_one({"_id": item_id}, {"_id": 0})
                return {**saved_item, "id": item_id_str}

        except Exception as e:
            logging.error({"Error creating/updating item": e})
            raise e

    async def get_item(self, value: str, key: str):
        try:
            db = await get_database()
            item = await db[self.model].find_one({key: value}, {"_id": 0})
            if item is None:
                return None
            return item
        except Exception as e:
            logging.error({"Error getting item": e})
            return None

    async def get_item_count(self, query={}):
        try:
            db = await get_database()
            item_count = await db[self.model].count_documents(query)
            return item_count
        except Exception as e:
            logging.error({"Error getting item count": e})
            return None

    async def get_items(self, query={}):
        try:
            db = await get_database()
            items = []
            async for item in db[self.model].find(query, {"_id": 0}):
                items.append(item)
            return items
        except Exception as e:
            logging.error(f"Error querying history_tasks: {str(e)}")
            return None
        
    async def get_items_aggregate(self, query={}):
        try:
            db = await get_database()
            pipeline = []

            if query:
                pipeline.append({"$match": query})

            # Sort by date in descending order within each group
            pipeline.append({"$sort": {"date": -1}})

            # Group by task_id and select the first document (highest date)
            pipeline.append({
                "$group": {
                    "_id": "$task_id",
                    "doc": {"$first": "$$ROOT"}
                }
            })

            # Exclude the _id field from the result
            pipeline.append({"$project": {"_id": 0}})

            items = []
            async for item in db[self.model].aggregate(pipeline):
                # Convert ObjectId to string
                item['doc']['_id'] = str(item['doc']['_id'])
                items.append(item['doc'])
            return items
        except Exception as e:
            logging.error(f"Error querying history_tasks: {str(e)}")
            return []


    async def get_items_with_ids(self, query={}):
        try:
            db = await get_database()
            items = []
            async for item in db[self.model].find(query):
                items.append(item)
            return items
        except Exception as e:
            logging.error(f"Error querying history_tasks: {str(e)}")
            return None

    async def get_items_paginate(self, query={}, skip: int = 0, limit: int = 50, sort_key = None):
        try:
            db = await get_database()
            items = []
            cursor = db[self.model].find(query, {
                "_id": 0
            }).skip(skip).limit(limit)
            if sort_key:
                cursor = cursor.sort([(sort_key, -1)])
            async for item in cursor:
                items.append(item)
            return items
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error retrieving items")

    async def get_distinct(self, field: str):
        try:
            db = await get_database()
            items = await db[self.model].distinct(field)
            return items
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error retrieving items")

    async def update_item(self, item_id: str, item: dict):
        try:
            db = await get_database()
            await db[self.model].update_one({"_id": item_id}, {"$set": item})
            updated_item = await db[self.model].find_one({"_id": item_id}, {"_id": 0})
            return updated_item
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error updating item")

    async def update_specific_field(
        self, item_id: str, field_name: str, field_value: dict
    ):
        try:
            db = await get_database()
            result = await db[self.model].update_one(
                {"id": item_id},
                {"$set": {field_name: field_value}},
                upsert=True,
            )

            updated_item = await db[self.model].find_one({"id": item_id})
            return {"updated_item": updated_item, "result": result}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating field: {e}")

    async def update_field_by_email(
        self, email: str, field_name: str, field_value: dict
    ):
        try:
            db = await get_database()

            # Use the email field for updating instead of _id
            result = await db[self.model].update_one(
                {"email": email},
                {"$set": {field_name: field_value}},
                upsert=True,
            )

            updated_item = await db[self.model].find_one({"email": email})
            return updated_item

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error updating field by email: {e}")
            raise e

    async def delete(self, value: str, key: str):
        try:
            db = await get_database()
            result = await db[self.model].delete_one({key: value})
            if result.deleted_count == 1:
                return {"message": f"{self.model} deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail=f"{self.model} not found")
        except Exception as e:
            logging.error(f"Error deleting item: {str(e)}")
            raise HTTPException(status_code=500, detail="Error deleting item")

    async def get_items_by_date_range(
        self,
        from_date: str,
        to_date: str,
        date_key: str,
        additional_key: str = None,
        additional_value: str = None,
    ):
        try:
            db = await get_database()

            # Convert date strings to datetime objects
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
            to_date = datetime.strptime(to_date, "%Y-%m-%d")

            # Adjust the to_date to the end of the day
            to_date = to_date + timedelta(days=1) - timedelta(seconds=1)

            # Log the adjusted date range for debugging
            logging.info(f"Adjusted Query Range: {from_date} to {to_date}")

            # Define the basic query for date range
            query = {date_key: {"$gte": from_date, "$lte": to_date}}

            # If additional key and value are provided, add them to the query
            if additional_key and additional_value:
                query[additional_key] = additional_value

            # Log the complete query for debugging
            logging.info(f"Complete Query: {query}")

            # Query items within the date range and additional key-value
            items = []
            async for item in db[self.model].find(query, {"_id": 0}):
                items.append(item)

            return items
        except Exception as e:
            logging.error(e)
            raise e

    async def clone_collection(self, original_collection: str, new_collection: str):
        try:
            db = await get_database()
            pipeline = [{"$out": new_collection}]
            await db[original_collection].aggregate(pipeline).next()
            return f"{original_collection} cloned to {new_collection} successfully"
        except Exception as e:
            logging.error(f"Error cloning collection: {str(e)}")
            raise HTTPException(status_code=500, detail="Error cloning collection")
        
    async def append_data_to_item(self, id: str, data):
        try:
            db = await get_database()
            updated_item = await db[self.model].find_one_and_update(
                {'task_id': id},
                {'$push': {'activities': data}},
                projection={'_id': False},
                return_document=True  # This ensures the updated document is returned
            )
            return updated_item
        except Exception as e:
            logging.error(f"Error appending new activity: {str(e)}")
            raise HTTPException(status_code=500, detail="Error appending new activity")
    
    async def new_update_specific_field(
        self, item_id: str, field_name: str, field_value: dict
    ):
        try:
            db = await get_database()
            result = await db[self.model].find_one_and_update(
                {"id": item_id},
                {"$set": {field_name: field_value}},
                # upsert=True,
            )

            updated_item = await db[self.model].find_one({"id": item_id})
            return {"updated_item": updated_item, "result": result}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating field: {e}")