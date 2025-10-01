import uvicorn
from app.core.config import global_config

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host=global_config.host, port=global_config.port, reload=True
    )
