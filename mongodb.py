import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("MONGODB_NAME")

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_database():
    if db.client is None:
        db.client = AsyncIOMotorClient(DATABASE_URL)
    return db.client[DATABASE_NAME]


async def close_database_connection():
    if db.client is not None:
        db.client.close()


async def check_db_connection():
    try:
        client = AsyncIOMotorClient(DATABASE_URL)
        await client.admin.command("ping")

        # Get the list of available collections in the database
        database = client[DATABASE_NAME]
        collection_names = await database.list_collection_names()

        # Log the available collections
        logging.info("Connected to the database.")
        logging.info("Available collections:")
        for collection_name in collection_names:
            logging.info(collection_name)

        return True
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        return False