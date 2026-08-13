from fastapi import FastAPI

app= FastAPI(title="Task Manager")


@app.get("/health")
def health_check():
    return{
        "status":"ok",
        "message":"API is running"
    }