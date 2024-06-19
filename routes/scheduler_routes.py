from fastapi import APIRouter, status
from services.scheduler_service import SchedulerService


schedular_service = SchedulerService()

schedular_router = APIRouter(
    prefix='/api/v1/schedular',
    tags=['Schedular']
)

@schedular_router.get('/', status_code=status.HTTP_200_OK)
async def get_tasks():
    return await schedular_service.fetch_tasks()

