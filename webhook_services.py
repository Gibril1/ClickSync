import os
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()
CLICKUP_API_KEY = os.getenv('CLICK_UP_API_KEY')

class WebHookServices:
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
    
    def convert_timestamp(self, timestamp):
        return datetime.fromtimestamp(float(int(timestamp)/1000))
    
    def get_task_details(self, task_id:str):
        url = f"https://api.clickup.com/api/v2/task/{task_id}"

        headers = {
        'Authorization': CLICKUP_API_KEY
        }

        response = requests.request("GET", url, headers=headers, data={})
        if response.status_code == 200:
            api_response = response.json()
            # # print(api_response)
            # print(type(api_response))
            # # return 1
        
            name = api_response.get("name", "")
            due_date = api_response.get("due_date", "")
            project = api_response.get("project", {}).get("name", "")
            time_estimate = api_response.get("time_estimate", "")
            priority = api_response.get("priority", {}).get("priority", "")
            collaborators = [assignee.get("email", "") for assignee in api_response.get("assignees", [])]
            status = api_response.get("status", "")

            current = {
                "name": name,
                "due_date": due_date,
                "project": project,
                "time_estimate": time_estimate,
                "priority": priority,
                "collaborators": collaborators,
                "status": status,
            }

            return current

        




    def handle_webhook(self, webhook_event):
        history_item = webhook_event["history_items"][0]
        field = history_item["field"]
        task_id = webhook_event["task_id"]
        event = webhook_event["event"]
        date = history_item["date"]
        update_by = history_item["user"]["email"]

        update = self.get_update_value(field, history_item)

        if update is not None:
            activity = {
                "event": event,
                "last_updated": self.convert_timestamp(date),
                "update_by": update_by,
                "update": {
                    field: update,
                    "date": self.convert_timestamp(date)
                },
                "task_id": task_id
            }
            current = self.get_task_details(task_id=task_id)
            return {
                'activity': activity,
                'current': current
            }

    