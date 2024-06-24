from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routes.webhook_routes import webhook_router
from routes.scheduler_routes import schedular_router
from routes.clickup_routes import clickup_router
from services.scheduler_service import SchedulerService
from mongodb import get_database
from pymongo import ASCENDING

# Scheduler setup
scheduler = AsyncIOScheduler()

# init schedule service
scheduler_service = SchedulerService()

# create unique index on collections
async def create_unique_index():
    db = await get_database()
    await db["events"].create_index([("event_id", ASCENDING)], unique=True)
    await db["task_activities"].create_index([("task_id", ASCENDING)], unique=True)

# Schedule tasks
def schedule_tasks():
    scheduler.add_job(scheduler_service.fetch_tasks, 'cron', hour=9, minute=15)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_unique_index()
    scheduler.start()
    schedule_tasks()
    yield
    scheduler.shutdown()

# Init app
app = FastAPI(lifespan=lifespan)

# register routes
app.include_router(webhook_router)
app.include_router(schedular_router)
app.include_router(clickup_router)

@app.get('/')
def root():
    return {"message": "Fast API server is running"}

