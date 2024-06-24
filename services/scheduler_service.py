from fastapi import FastAPI
from datetime import datetime
import logging
import requests
from services.mongo_crud_service import MongoDBCRUDService
from services.webhook_services import WebHookServices
from services.clickup_service import ClickUpServices
from config import env_variables

app = FastAPI()

CLICKUP_API_KEY = env_variables.get("CLICKUP_API_KEY")
CLICKUP_TEAM_ID = env_variables.get("TEAM_ID")
LIST_ID = env_variables.get("LIST_ID")


# tasks activities
tasks_activities = MongoDBCRUDService("task_activities")
# webhook
webhook_services = WebHookServices()
clickup_service = ClickUpServices()

# init logging
logging.basicConfig(level=logging.INFO)


class SchedulerService:
    async def fetch_tasks(self):
        logging.info(f'********The schedular is running today at {datetime.now()}**********')
        clickup_tasks = clickup_service.get_all_tasks()
        
        tasks = [] # container

        
        # this holds tasks from clickup
        for clickup_task in clickup_tasks:
            task_id = clickup_task.get("id", "")
            name = clickup_task.get("name", "")
            last_updated = webhook_services.convert_timestamp(clickup_task.get("date_updated", 0))
            due_date = webhook_services.convert_timestamp(clickup_task.get("due_date", 0))
            time_estimate = clickup_task.get("time_estimate", "")
            priority = clickup_task.get("priority", {})
            
            if isinstance(priority, dict):
                priority = priority.get("priority", "")
            else:
                priority = None
            collaborators = [assignee.get("email", "") for assignee in clickup_task.get("assignees", [])]
            status = clickup_task.get("status", "")

            if isinstance(status, dict):
                status = status.get("status", "")
            else:
                status = None
            space_id = clickup_task.get("space", "").get("id", "")

            # get the project name from the space ID
            project = clickup_service.get_space_name(space_id=space_id)
            current = {
                "task_id": task_id,
                "name": name,
                "due_date": due_date,
                "time_estimate": time_estimate,
                "priority": priority,
                "status": status,
                "project": project,
                "collaborators": collaborators,
            }
            tasks.append(current)
        # return tasks
        
        for task in tasks:
            # check if this task exists in the database
            task_in_collection = await tasks_activities.get_item(task["task_id"], "task_id")
            # if it exists, update the current object
            if task_in_collection:
                # print(task_in_collection)
                logging.info("Task exists in collection so we update the current field")
                await tasks_activities.new_update_specific_field(task["task_id"], "current", current)
            else: # if it does not exist, it means task has not been recorded
                logging.info("Task does not exist in collection so we add a new document")
                new_updates = {
                "task_id": task["task_id"],
                "last_updated": last_updated,
                'activities': [],
                'current': task
            }
                
                new_task = await tasks_activities.create_item(new_updates)
                logging.info("Task has been created")
        return "Scheduler has completed"
                

        
        

        





