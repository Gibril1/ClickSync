from fastapi import Request, status, APIRouter
from services.webhook_services import WebHookServices
import logging

# Init Services
webhook_service = WebHookServices()

webhook_router = APIRouter(
    prefix='/api/v1/webhook',
    tags=['Webhook']
)

# init logging
logging.basicConfig(level=logging.INFO)


@webhook_router.post('/mediboard', status_code=status.HTTP_200_OK)
async def mediboard_events(req: Request):
    logging.info("Webhook has touched  the endpoint")
    webhook_event = await req.json()
    
    event_id = webhook_event["history_items"][0]["id"]

    # check if this event exists
    event = await webhook_service.find_event(event_id=event_id)
    if event:
        logging.info("Function has stopped because, the event has already been processed")
        return 
    
    # if the event has not been handled, continue with the processing
    logging.info('Function is being processed because this event has not been handled')
    await webhook_service.handle_webhook(webhook_event=webhook_event)
    
    
 
