from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import requests
from services.mongo_crud_service import MongoDBCRUDService
from config import env_variables

app = FastAPI()

CLICKUP_API_KEY = env_variables.get("CLICKUP_API_KEY")
CLICKUP_TEAM_ID = env_variables.get("TEAM_ID")
LIST_ID = env_variables.get("LIST_ID")

# Scheduler setup
scheduler = AsyncIOScheduler()

# tasks activities
tasks_activities = MongoDBCRUDService("tasks_activities")

# init logging
logging.basicConfig(level=logging.INFO)


class SchedulerService:
    async def fetch_tasks(self):
        url = "https://api.clickup.com/api/v2/list/901505655029/task"

        payload = {}
        headers = {
        'Authorization': 'pk_74411095_8383WZWCXRGCTHS3ZHWSQQC4X65SRQO9'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        tasks = []

        # this holds tasks from clickup
        clickup_tasks = response.json()["tasks"]
        for clickup_task in clickup_tasks:
            task_id = clickup_task.get("id", "")
            name = clickup_task.get("name", "")
            due_date = clickup_task.get("due_date", "")
            project = clickup_task.get("project", {}).get("name", "")
            time_estimate = clickup_task.get("time_estimate", "")
            priority = clickup_task.get("priority", {}).get("priority", "")
            collaborators = [assignee.get("email", "") for assignee in clickup_task.get("assignees", [])]
            status = clickup_task.get("status", "").get("status", "")

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
                logging.info("Task exists in collection so we update the current field")
                await tasks_activities.update_specific_field(task["task_id"], "current", current)
            else: # if it does not exist, it means task has not been recorded
                logging.info("Task does not exist in collection so we add a new document")
                new_updates = {
                "task_id": task["task_id"],
                "last_updated": due_date,
                'activities': [],
                'current': current
            }
                await tasks_activities.create_item(new_updates)
        return "Scheduler has finished running"
                

        
        

        

# async def fetch_task_updates():
#     end_time = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))  # Today at 00:00
#     start_time = end_time - datetime.timedelta(days=1)  # Yesterday at 00:00

#     async with httpx.AsyncClient() as client:
#         response = await client.get(
#             f"https://api.clickup.com/api/v2/team/{CLICKUP_TEAM_ID}/task",
#             headers=headers,
#             params={
#                 "start_date": int(start_time.timestamp() * 1000),  # Convert to milliseconds
#                 "end_date": int(end_time.timestamp() * 1000),  # Convert to milliseconds
#             },
#         )
#         tasks = response.json()["tasks"]

#         for task in tasks:
#             existing_task = await tasks_collection.find_one({"id": task["id"]})
#             if not existing_task:
#                 await tasks_collection.insert_one(task)
#             else:
#                 await tasks_collection.update_one({"id": task["id"]}, {"$set": task})
#     logging.info("Task updates fetched")
    
# @app.on_event("startup")
# async def startup_event():
#     # Schedule tasks
#     scheduler.add_job(fetch_task_updates, "interval", minutes=1)
#     scheduler.start()

# @app.on_event("shutdown")
# async def shutdown_event():
#     scheduler.shutdown()

# @app.get("/")
# async def root():
#     return {"message": "Scheduler for ClickUp task updates is running"}




