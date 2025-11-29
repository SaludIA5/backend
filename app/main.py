import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from limits import parse
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter
from slowapi.util import get_remote_address

from app.api.router import router
from app.core.config import global_config
from app.params import FRONTEND_PORT, FRONTEND_URL

logging.basicConfig(level=logging.INFO)

memory_storage = MemoryStorage()
limiter_strategy = FixedWindowRateLimiter(memory_storage)
global_limit = parse("60/minute")

app = FastAPI(
    title=global_config.title,
    version=global_config.version,
    description=global_config.description,
    openapi_url=f"{global_config.api_prefix}{global_config.openapi_url}",
    docs_url=global_config.docs_url,
    redoc_url=global_config.redoc_url,
)


@app.middleware("http")
async def global_rate_limit_middleware(request: Request, call_next):
    ip = get_remote_address(request)

    if not limiter_strategy.test(global_limit, ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded: 60 requests per minute"},
        )

    limiter_strategy.hit(global_limit, ip)
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"{FRONTEND_URL}:{FRONTEND_PORT}",
        "https://saludia5.pages.dev",
        "https://develop.saludia5.pages.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "Cookie", "*"],
    expose_headers=["*"],
)

app.include_router(router, prefix=global_config.api_prefix)


@app.get("/")
def read_root():
    welcome_message: str = f"SALUAI5 - Backend - {datetime.now().year}"
    return {"message": welcome_message}


@app.api_route("/health", methods=["GET", "HEAD"])
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    print(global_config.port)
    uvicorn.run(
        "app.main:app", host=global_config.host, port=global_config.port, reload=True
    )
