from contextlib import contextmanager

from fastapi import Depends, FastAPI
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session

from com_agent.api.routers.chat import router as chat_router
from com_agent.database.connection import Base, engine, get_db

app = FastAPI()

app.include_router(chat_router, prefix="/api")


@contextmanager
def lifespan(app: FastAPI):
    with engine.begin() as conn:
        Base.metadata.create_all(conn)
    yield


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Commercial Agent Bot API",
        version="1.0.0",
        description="API para el chatbot de agente comercial",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
async def root(db: Session = Depends(get_db)):
    return {
        "message": "Welcome to the Commercial Agent Bot API",
        "db_status": "conectado",
    }
