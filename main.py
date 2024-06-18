from fastapi import FastAPI
from routes import webhook_router

# Init app
app = FastAPI()

# register routes
app.include_router(webhook_router)


@app.get('/')
def root():
    return "Fast API server is running"

   
