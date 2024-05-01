import uvicorn
from fastapi import FastAPI
from routers import data, upload_data, map
from contextlib import asynccontextmanager
from default_map import create_default_map


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_default_map()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(data.router)
app.include_router(upload_data.router)
app.include_router(map.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
