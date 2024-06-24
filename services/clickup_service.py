import json
import os
import asyncio
import logging
from datetime import datetime, timedelta
import requests
from config import env_variables
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()
CLICKUP_API_KEY = env_variables.get("CLICKUP_API_KEY")
CLICKUP_TEAM_ID = env_variables.get("TEAM_ID")

logger = logging.getLogger(__name__)

class ClickUpClient:
    def __init__(self, token: str = None):
        self.token = token or CLICKUP_API_KEY

    async def send_request(self, url, method="GET", params=None, data=None, json=None, headers=None, max_retries=3):
        headers = headers or {
            "Authorization": self.token,
            "Content-Type": "application/json",
        }
        retry_delay = 15  # Initial retry delay in seconds
        for _ in range(max_retries):
            try:
                if method == "GET":
                    response = requests.get(url, params=params, headers=headers)
                elif method == "POST":
                    response = requests.post(url, params=params, data=data, json=json, headers=headers)
                elif method == "DELETE":
                    response = requests.delete(url, headers=headers)
                
                if response.status_code == 429:
                    # Handle 429 Too Many Requests error by retrying
                    logger.info(
                        f"Request failed with status code 429, retrying in {retry_delay} seconds"
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                elif response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )
                else:
                    return response.json()
            except HTTPException as e:
                    # raise  # Propagate HTTPException for non-429 errors
                    logger.error(f"Request failed, status code {e.status_code}: {str(e)}", e)
            except Exception as e:
                # Handle other exceptions (e.g., network issues)
                logger.error(f"Request failed: {str(e)}", e)
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
class ClickUpServices:
    def __init__(self, token: str = None, team_id: str = None) -> None:
        self.client = ClickUpClient(token=token)
        if team_id is None:
            self.team_id = CLICKUP_TEAM_ID
        else:
            self.team_id = team_id

    # get all the details of a task
    def get_task_details(self, task_id: str):
        url = f"https://api.clickup.com/api/v2/task/{task_id}"

        headers = {
        'Authorization': CLICKUP_API_KEY
        }

        response = requests.request("GET", url, headers=headers, data={})
        # response = self.client.send_request(url)

        

        return response.json()


    # fetch all tasks from certain spaces that where last updated at a particular time
    def get_all_tasks(self):
        url = "https://api.clickup.com/api/v2/team/" + self.team_id + "/task"

        headers = {
        'Authorization': CLICKUP_API_KEY
        }


        # Calculate the datetime for yesterday
        yesterday = datetime.now() - timedelta(days=1)

        # Set the time to 9:15 AM
        yesterday_915am = yesterday.replace(hour=9, minute=15, second=0, microsecond=0)

        # Convert to Unix timestamp
        unix_timestamp = int(yesterday_915am.timestamp())
        
        query={
            "date_updated_gt": unix_timestamp,
            "include_closed": True,
            "subtasks": True,
            "space_ids":["90030312574", "90080539685", "90030470033"]
        }

        response = requests.request("GET", url=url, headers=headers, params=query)
        # response = await self.client.send_request(url, params=query)
        return response.json()["tasks"]
    

    def get_space_name(self, space_id:str):
        url = f"https://api.clickup.com/api/v2/space/{space_id}"

        headers = {
        'Authorization': CLICKUP_API_KEY
        }

        response = requests.request("GET", url=url, headers=headers, data={})

        space_name = response.json()["name"]

        return space_name

    
    