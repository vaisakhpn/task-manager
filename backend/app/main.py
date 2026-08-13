from fastapi import FastAPI

from app.core.config import settings

app= FastAPI(title=settings.PROJECT_NAME,
             debug=settings.DEBUG)


@app.get("/health")
def health_check():
   return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "project_name": settings.PROJECT_NAME,
    }