from fastapi import Request, status, APIRouter
from services.webhook_services import WebHookServices
from services.clickup_service import ClickUpServices
import logging

# Init Services
webhook_service = WebHookServices()
clickup_service = ClickUpServices()

webhook_router = APIRouter(
    prefix='/api/v1/webhook',
    tags=['Webhook']
)

# init logging
logging.basicConfig(level=logging.INFO)



    
@webhook_router.post('/clickup_webhook', status_code=status.HTTP_200_OK)
async def mediboard_events(req: Request):
    logging.info("Webhook has touched  the endpoint")
    webhook_event = await req.json()

    event_id = webhook_event["history_items"][0]["id"]
    valid_space_ids = ["90030312574", "90080539685", "90030470033"]
     
 
    space_id = clickup_service.get_task_details(webhook_event["task_id"])["space"]["id"]

    # check to see if the event is on task that is in a valid project
    if space_id not in valid_space_ids:
        logging.info("Events from this space are not going to be handled")
        return
    
    # check if this event exists
    event = await webhook_service.find_event(event_id=event_id)
    if event:
        logging.info("Function has stopped because, the event has already been processed")
        return 
    
    # if the event has not been handled, continue with the processing
    logging.info('Function is being processed because this event has not been handled')
    await webhook_service.handle_webhook(webhook_event=webhook_event)
 
 
