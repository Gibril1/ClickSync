import os
from dotenv import load_dotenv

load_dotenv()

env_variables = {
    "CLICKUP_API_KEY" : os.getenv("CLICK_UP_API_KEY"),
    "TEAM_ID" : os.getenv("TEAM_ID"),
    "LIST_ID" : os.getenv("LIST_ID"),

}