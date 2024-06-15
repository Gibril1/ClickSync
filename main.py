from fastapi import FastAPI, status, Request

app = FastAPI()


@app.get('/')
def root():
    return "Fast API server is running"

@app.post('/mediboard', status_code=status.HTTP_200_OK)
def mediboard_events(event:Request):
    print(event)

