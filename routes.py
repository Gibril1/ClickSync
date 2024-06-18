from fastapi import Request, status, APIRouter
from webhook_services import WebHookServices

# Init Services
webhook_service = WebHookServices()

webhook_router = APIRouter(
    prefix='/api/v1/webhook',
    tags=['Webhook']
)

@webhook_router.post('/mediboard', status_code=status.HTTP_200_OK)
async def mediboard_events(req: Request):
    webhook_event = await req.json()
    print(webhook_service.handle_webhook(webhook_event=webhook_event))
    return webhook_service.handle_webhook(webhook_event=webhook_event)
 
