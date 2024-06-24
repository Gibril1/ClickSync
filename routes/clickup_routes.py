from fastapi import Request, status, APIRouter
from services.clickup_service import ClickUpServices
import logging

# Init Services
clickup_service = ClickUpServices()

clickup_router = APIRouter(
    prefix='/api/v1/clickup',
    tags=['Clickup API']
)

@clickup_router.get('/', status_code=status.HTTP_200_OK)
def get_task_details(task_id:str):
    return clickup_service.get_task_details(task_id=task_id)


@clickup_router.get('/tasks', status_code=status.HTTP_200_OK)
def get_tasks():
    return clickup_service.get_all_tasks()

@clickup_router.get('/space_name', status_code=status.HTTP_200_OK)
def get_space_name(space_id:str):
    return clickup_service.get_space_name(space_id=space_id)