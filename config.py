import os
from dotenv import load_dotenv

load_dotenv()

env_variables = {
    "CLICKUP_API_KEY" : os.getenv("RGT_CLICKUP_API_KEY"),
    "TEAM_ID" : os.getenv("RGT_TEAM_ID"),
    "DATABASE_URL" : os.getenv("MONGODB_URL"),
    "DATABASE_NAME" : os.getenv("MONGODB_NAME")
}