from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from strawberry.asgi import GraphQL
from sqlalchemy import select, text
from .db.connection import DBConnection
from .schema import schema

gql = GraphQL(schema=schema)

@asynccontextmanager
async def lifespan(app):
    yield
    if (DBConnection.is_initialized()):
        await DBConnection.get().engine().dispose()

async def ping(_):
    try:
        async with DBConnection.get().session() as session:
            await session.execute(text("SELECT 1"))
        return JSONResponse({
            "status": "OK"
        })
    except Exception as e:
        return JSONResponse({
            "status": "ERROR",
            "message": str(e)
        }, status_code=500)

app = Starlette(lifespan=lifespan)
app.add_route("/ping", ping)
app.add_route("/", gql)