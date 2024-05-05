import uvicorn
from fastapi import FastAPI
from routers import data, upload_data, map
from contextlib import asynccontextmanager
from cache.cache_maps import cache_maps
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache_maps()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(data.router)
app.include_router(upload_data.router)
app.include_router(map.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
