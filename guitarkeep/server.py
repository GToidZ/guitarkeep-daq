import asyncio
from starlette.applications import Starlette
from strawberry.asgi import GraphQL
from .db.connection import DBConnection

app = GraphQL()

server = Starlette()
server.add_route("/graphql", app)