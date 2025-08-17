from fastapi import FastAPI

from .db import init_db
from .routers import analytics, moderation

app = FastAPI(title="Smart Content Moderator API")

app.include_router(moderation.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def on_startup():
    await init_db()
