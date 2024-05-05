import uvicorn
from fastapi import FastAPI
from routers import data, upload_data, map
from contextlib import asynccontextmanager
from cache.cache_maps import cache_maps
from cache.cache_graphs import cache_graphs, router
from fastapi.staticfiles import StaticFiles
from subapp import graph_manager
from fastapi.middleware.wsgi import WSGIMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache_maps()
    await cache_graphs()
    sub_apps = graph_manager.get_apps()
    for sub_app_path, sub_app in sub_apps.items():
        app.mount(sub_app_path, WSGIMiddleware(sub_app.server))
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(data.router)
app.include_router(upload_data.router)
app.include_router(map.router)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
