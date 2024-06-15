from fastapi import FastAPI, status, Request

app = FastAPI()


@app.get('/')
def root():
    return "Fast API server is running"

@app.post('/mediboard', status_code=status.HTTP_200_OK)
async def mediboard_events(req:Request):
    event = await req.json()
    print(event)

