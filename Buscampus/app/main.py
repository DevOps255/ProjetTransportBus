from core.database import create_mod
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from Auth.services.routers.user_router import router as auth_router, limiter
from Auth.services.routers.api_keys_router import router as api_router, limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    #pour exécuter la base de donnee en SQLite. Alembic gère très bien les migrations 
    await create_mod()
    yield
    
app = FastAPI(title="Auth JWT & API keys", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)
app.include_router(api_router)

