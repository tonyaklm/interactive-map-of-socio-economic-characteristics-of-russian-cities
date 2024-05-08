import uvicorn
from fastapi import FastAPI, Request
from routers import update, post, map, delete
from contextlib import asynccontextmanager
from cache.cache_maps import cache_maps
from cache.cache_graphs import cache_graphs
from fastapi.staticfiles import StaticFiles
from subapp import graph_manager
from fastapi.middleware.wsgi import WSGIMiddleware
import os
from fastapi.responses import RedirectResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache_maps()
    await cache_graphs()
    sub_apps = graph_manager.get_apps()
    for sub_app_path, sub_app in sub_apps.items():
        app.mount(sub_app_path, WSGIMiddleware(sub_app.get_app().server))
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(update.router)
app.include_router(post.router)
app.include_router(map.router)
app.include_router(delete.router)


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     if request.cookies.get('access_token_cookie') is None:
#         url = f'http://{os.getenv("INTERNAL_ADDRESS")}:{os.getenv("USER_SERVICE_PORT")}/login/'
#         return RedirectResponse(url=url)
#     response = await call_next(request)
#     if request.cookies.get('access_token_cookie') is None:
#         url = f'http://{os.getenv("INTERNAL_ADDRESS")}:{os.getenv("USER_SERVICE_PORT")}/login/'
#         return RedirectResponse(url=url)
#     return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
