import pandas as pd
from fastapi import APIRouter, File, UploadFile, Request, status, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from routers.data import create_column, update_data
from sqlalchemy.ext.asyncio import AsyncSession
from utils.session import get_session
from io import BytesIO
from sqlalchemy import types
from models.data_models import CreateColumn, UpdateData

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/upload_file")


@router.post("/")
async def index(file: UploadFile = File(...), column_type: str = Form(...),
                session: AsyncSession = Depends(get_session)):
    if file:
        new_data = pd.read_csv(BytesIO(file.file.read()))
        new_column_name = new_data.columns[1]
        new_column_type = column_type
        response = await create_column(CreateColumn(column_name=new_column_name, column_type=new_column_type),
                                       session)
        for index, row in new_data.iterrows():
            response = await update_data(
                UpdateData(data_id=row['id'], column=new_column_name, new_value=row[new_column_name]),
                session)

        return RedirectResponse(url="/upload_file", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(name="index.html", context={"request": file})


@router.get("/")
async def get_upload_form(request: Request):
    camel_case_types = []
    for attribute in dir(types):
        if attribute != attribute.upper() and hasattr(getattr(types, attribute), '__visit_name__'):
            camel_case_types.append(attribute)

    return templates.TemplateResponse(name="index.html", context={"request": request, "selected": camel_case_types})
