import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.config.app_config import AppConfig

from src.app.features.auth.presentation.web.routes.user_routes import router as user_router
from src.app.features.auth.presentation.web.routes.password_reset_routes import router as password_reset_router
from src.app.features.auth.presentation.web.routes.email_verification_routes import router as email_verification_router
from src.app.features.projects.presentation.web.routes.project_routes import router as project_router
from src.app.features.notes.presentation.web.routes.note_routes import project_notes_router, notes_router
from src.app.features.tasks.presentation.web.routes.task_routes import project_tasks_router, tasks_router

ENV = os.getenv("APP_ENV", "local")

config = AppConfig.instance()
app_name = config.get_config("app.name")
app_version = config.get_config("app.version")

fastApiApp = FastAPI(title=app_name, version=app_version)

if ENV not in ("local", "container"):
    fastApiApp.docs_url = None
    fastApiApp.redoc_url = None
    fastApiApp.openapi_url = None

# --- CORS Origins from config ---
origins = [
    "http://localhost:5173",
    "http://localhost:*",
]

fastApiApp.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@fastApiApp.get("/")
def read_root():
    return {"message": "Welcome to the API"}


@fastApiApp.get("/health")
def get_health_check():
    return "Ok"

# TODO validate best practices for endpoint naming conventions
fastApiApp.include_router(user_router, prefix="/api/v1/auth", tags=["Auth"])
fastApiApp.include_router(password_reset_router, prefix="/api/v1/auth/reset-password", tags=["Password Reset"])
fastApiApp.include_router(email_verification_router, prefix="/api/v1/auth", tags=["Email Verification"])
fastApiApp.include_router(project_router, prefix="/api/v1/projects", tags=["Projects"])
fastApiApp.include_router(project_notes_router, prefix="/api/v1/projects", tags=["Notes"])
fastApiApp.include_router(notes_router, prefix="/api/v1/notes", tags=["Notes"])
fastApiApp.include_router(project_tasks_router, prefix="/api/v1/projects", tags=["Tasks"])
fastApiApp.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks"])