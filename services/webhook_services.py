import os
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv
import requests

from services.mongo_crud_service import MongoDBCRUDService
task_activities = MongoDBCRUDService("task_activities")
events = MongoDBCRUDService("events")

load_dotenv()
CLICKUP_API_KEY = os.getenv('CLICK_UP_API_KEY')

class WebHookServices:
    async def add_task_activities(self, data):
        new_data = await task_activities.create_item(data)
        return new_data
    
    async def check_if_task_exists(self, task_id):
        return await task_activities.get_item(task_id, "task_id")

    def get_update_value(self, field, history_item):
        if field == 'priority':
            return history_item.get("after", {}).get(field)
        elif field == 'due_date':
            return history_item.get("after")
        elif field == 'assignee_add':
            return history_item.get("after", {}).get("email")
        elif field == 'assignee_rem':
            return history_item.get("before", {}).get("email")
        elif field == 'name':
            return history_item.get("after")
        elif field == 'comment':
            return history_item.get("comment", [{}])[0].get("text")
        elif field == 'status':
            return history_item.get("after")
        return None
    
    def convert_timestamp(self, timestamp:str):
        if not timestamp:
            return None
        convertible_timeformat = int(timestamp) / 1000
        return datetime.fromtimestamp(convertible_timeformat)
    
    def get_task_details(self, task_id:str):
        url = f"https://api.clickup.com/api/v2/task/{task_id}"

        headers = {
        'Authorization': CLICKUP_API_KEY
        }

        response = requests.request("GET", url, headers=headers, data={})
        if response.status_code == 200:
            api_response = response.json()
            
            # get the needed fields
            name = api_response.get("name", "")
            due_date = api_response.get("due_date", "")
            project = api_response.get("project", {}).get("name", "")
            time_estimate = api_response.get("time_estimate", "")
            priority = api_response.get("priority", {}).get("priority", "")
            collaborators = [assignee.get("email", "") for assignee in api_response.get("assignees", [])]
            status = api_response.get("status", "").get("status", "")

            current = {
                "name": name,
                "due_date": due_date,
                "time_estimate": time_estimate,
                "priority": priority,
                "status": status,
                "project": project,
                "collaborators": collaborators,
            }

            return current

    async def handle_webhook(self, webhook_event):
        # retrieve some fields from the webhook event
        history_item = webhook_event["history_items"][0]
        field = history_item["field"]
        task_id = webhook_event["task_id"]
        event = webhook_event["event"]
        date = self.convert_timestamp(history_item["date"])
        update_by = history_item["user"]["email"]
        event_id = webhook_event["history_items"][0]["id"]

        # check if this event has already happened
        event_object = await self.find_event(event_id=event_id)
        if event_object:
            return 1
        
        # add the new event
        await self.add_events_to_database(event_id=event_id)
        

        # get the real update of what happened
        update = self.get_update_value(field, history_item)

        # structure the task activity
        if update is not None:
            new_activity = {
                "update_by": update_by,
                "date": date,
                "update": {
                    field: update,
                    "date": date
                },
                "event": event,
            }

            # check if the task already exists in the database
            task = await self.check_if_task_exists(task_id=task_id)
            if task is not None:
                activities = task["activities"]
                
                for activity in activities:
                    if activity["update"] == new_activity["update"]:
                        return
                # append the new activity to it
                updated_task = await task_activities.append_data_to_item(task_id, new_activity)
                return updated_task
            # elif task is None:
            current = self.get_task_details(task_id=task_id)

            new_updates = {
                "task_id": task_id,
                "last_updated": date,
                'activities': [new_activity],
                'current': current
            }

            new_task = await self.add_task_activities(data=new_updates)
            return new_task
    
    # add events to the database
    async def add_events_to_database(self, event_id:str):
        try:
            event = {
                "event_id": event_id
            }
            return await events.create_item(event)
        except Exception as e:
            return
    
    # check if that event exists in the database
    async def find_event(self, event_id:str):
        return await events.get_item(event_id, "event_id")



    
    
    
    

    