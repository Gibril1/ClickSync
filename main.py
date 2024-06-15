from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def root():
    return "Fast API server is running"
