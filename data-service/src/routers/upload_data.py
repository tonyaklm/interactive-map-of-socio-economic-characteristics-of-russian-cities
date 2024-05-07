from typing import Optional

import pandas as pd
from fastapi import APIRouter, File, UploadFile, Request, status, Depends, Form, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from routers.data import create_column, update_data
from sqlalchemy.ext.asyncio import AsyncSession
from utils.session import get_session
from io import BytesIO
from sqlalchemy import types
from models.data_models import CreateColumn, UpdateData
from fastapi import HTTPException
from cache.cache_maps import cache_map
import os

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/upload_data")


@router.post("/")
async def index(file: UploadFile = File(...), column_type: str = Form(...),
                session: AsyncSession = Depends(get_session)):
    if file:
        new_data = pd.read_csv(BytesIO(file.file.read()))
        new_column_name = new_data.columns[1]
        new_column_type = column_type
        try:
            response = await create_column(CreateColumn(column_name=new_column_name, column_type=new_column_type),
                                           session)
        except HTTPException:
            return RedirectResponse(url="/upload_data", status_code=status.HTTP_303_SEE_OTHER)
        for index, row in new_data.iterrows():
            try:
                response = await update_data(
                    UpdateData(data_id=row['id'], column=new_column_name, new_value=row[new_column_name]),
                    session)
            except HTTPException:
                return RedirectResponse(url="/upload_data", status_code=status.HTTP_303_SEE_OTHER)
        await cache_map(new_column_name, session)

        return RedirectResponse(url="/upload_data", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(name="upload_file.html", context={"request": file})


@router.get("/")
async def get_upload_form(request: Request, access_token_cookie: Optional[str] = Cookie(default=None)):
    if access_token_cookie == None:
        url = f'http://{os.getenv("INTERNAL_ADDRESS")}:{os.getenv("USER_SERVICE_PORT")}/login/'
        return RedirectResponse(url=url)
    camel_case_types = []
    for attribute in dir(types):
        if attribute != attribute.upper() and hasattr(getattr(types, attribute), '__visit_name__'):
            camel_case_types.append(attribute)

    return templates.TemplateResponse(name="upload_file.html", context={"request": request, "types": camel_case_types})
