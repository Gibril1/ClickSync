import os
import asyncio
import logging
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv

from config import env_variables

load_dotenv()

# get env variables
CLICKUP_API_KEY = env_variables.get('CLICKUP_API_KEY')
TEAM_ID = env_variables.get('TEAM_ID')

logger = logging.getLogger(__name__)
class ClickUpClient:
    def __init__(self, token: str = None):
        self.token = token or CLICKUP_API_KEY

    async def send_request(
        self, url, method="GET", params=None, data=None, json=None, headers=None, max_retries=3
    ):
        headers = headers or {
            "Authorization": self.token,
            "Content-Type": "application/json",
        }
        retry_delay = 15  # Initial retry delay in seconds

        for _ in range(max_retries):
            async with httpx.AsyncClient(timeout=15) as client:
                try:
                    if method == "GET":
                        response = await client.get(url, params=params, headers=headers)
                    elif method == "POST":
                        response = await client.post(
                            url, params=params, data=data, json=json, headers=headers
                        )
                    elif method == "DELETE":
                        response = await client.delete(url, headers=headers)

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

        # If max retries are exhausted without success, raise an exception
        raise Exception("Max retries reached, request still failed")
    

class ClickUpService:
    def __init__(self, token: str = None, team_id: str = None):
        self.client = ClickUpClient(token=token)
        if team_id is None:
            self.team_id = TEAM_ID
        else:
            self.team_id = team_id
    
    async def get_task_status_history(self, task_id: str):
        url = "https://api.clickup.com/api/v2/task/" + task_id + "/time_in_status"
        response = await self.client.send_request(url)
        return response

    async def get_tasks(self, list_id, collection_name, include_subtasks=True):
        url = "https://api.clickup.com/api/v2/list/" + list_id + "/task"

        query = {
            "subtasks": include_subtasks,
        }

        logger.info(f"Getting tasks from ClickUp with list_id: {list_id}")
        tasks = await self.client.send_request(url, params=query)
        if tasks.get("tasks"):
            if not tasks["tasks"]:
                logger.info(f"Got 0 tasks from ClickUp with list_id: {list_id}")
                return []
            logger.info(
                f"Got {len(tasks['tasks'])} tasks from ClickUp with list_id: {list_id}"
            )
            tasks = tasks["tasks"]
            return tasks
        else:
            logger.info(f"Got 0 tasks from ClickUp with list_id: {list_id}")
            return []
    
    
        
