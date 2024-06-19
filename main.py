from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes.webhook_routes import webhook_router
from routes.scheduler_routes import schedular_router
from mongodb import get_database
from pymongo import ASCENDING

async def create_unique_index():
    db = await get_database()
    await db["events"].create_index([("event_id", ASCENDING)], unique=True)
    await db["task_activities"].create_index([("task_id", ASCENDING)], unique=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_unique_index()
    yield

# Init app
app = FastAPI(lifespan=lifespan)

# register routes
app.include_router(webhook_router)
app.include_router(schedular_router)


@app.get('/')
def root():
    return "Fast API server is running"

   
