from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import auth, task, users

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# Configure CORS origins allowed to talk to our API
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(task.router, prefix="/tasks", tags=["Tasks"])



@app.get("/health")
def health_check():
   return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "project_name": settings.PROJECT_NAME,
    }
