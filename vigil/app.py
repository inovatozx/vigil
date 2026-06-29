from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from core.config import get_settings
from core.database import Base, engine
from core.middleware import setup_middlewares
from routes import (
    auth_routes,
    chat_routes,
    model_routes,
    session_routes,
    research_routes,
    agent_routes,
    document_routes,
    note_routes,
    task_routes,
    memory_routes,
    search_routes,
    gallery_routes
)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if not exist).")
    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, description="Vigil AI Workspace", lifespan=lifespan)
setup_middlewares(app)

app.include_router(auth_routes.router, prefix="/api", tags=["Auth"])
app.include_router(chat_routes.router, prefix="/api", tags=["Chat"])
app.include_router(model_routes.router, prefix="/api", tags=["Models"])
app.include_router(session_routes.router, prefix="/api", tags=["Sessions"])
app.include_router(research_routes.router, prefix="/api", tags=["Research"])
app.include_router(agent_routes.router, prefix="/api", tags=["Agent"])
app.include_router(document_routes.router, prefix="/api", tags=["Documents"])
app.include_router(note_routes.router, prefix="/api", tags=["Notes"])
app.include_router(task_routes.router, prefix="/api", tags=["Tasks"])
app.include_router(memory_routes.router, prefix="/api", tags=["Memory"])
app.include_router(search_routes.router, prefix="/api", tags=["Search"])
app.include_router(gallery_routes.router, prefix="/api", tags=["Gallery"])

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/static/index.html")

app.mount("/static", StaticFiles(directory="static", html=True), name="static")
