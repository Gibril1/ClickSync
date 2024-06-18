from fastapi import FastAPI, status, Request
from datetime import datetime
from services import WebHookServices

# Init app
app = FastAPI()

# services
webhook_service = WebHookServices()

@app.get('/')
def root():
    return "Fast API server is running"

@app.post('/mediboard', status_code=status.HTTP_200_OK)
async def mediboard_events(req: Request):
    webhook_event = await req.json()
    return webhook_service.handle_webhook(webhook_event=webhook_event)
    
