import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import global_config
from app.params import FRONTEND_PORT, FRONTEND_URL

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title=global_config.title,
    version=global_config.version,
    description=global_config.description,
    openapi_url=f"{global_config.api_prefix}{global_config.openapi_url}",
    docs_url=global_config.docs_url,
    redoc_url=global_config.redoc_url,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"{FRONTEND_URL}:{FRONTEND_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=global_config.api_prefix)


@app.get("/")
def read_root():
    welcome_message: str = f"SALUAI5 - Backend - {datetime.now().year}"
    return {"message": welcome_message}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    print(global_config.port)
    uvicorn.run(
        "app.main:app", host=global_config.host, port=global_config.port, reload=True
    )
