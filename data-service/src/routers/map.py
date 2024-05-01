from fastapi import APIRouter, Request, Depends, Query, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from utils.map import add_colorbar, add_circle_marker, color_region_by_id
from routers.data import get_column_names, get_indicator
from utils.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from default_map import get_folium_map

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix='/map')


@router.get("/")
async def render_map(request: Request, session: AsyncSession = Depends(get_session)):
    data = await get_indicator("population", session)
    folium_map = get_folium_map()
    colormap = add_colorbar(data, folium_map, "Population")
    for row in data:
        add_circle_marker(row, folium_map, "Population", colormap)

    folium_map.save("templates/map.html")

    # return render_template('index.html', selected='Empty Map')
    columns = await get_column_names(session)
    return templates.TemplateResponse(name="index.html",
                                      context={"request": request, "columns": columns['column_names'],
                                               "groups": columns['column_types']})


@router.get('/indicator')
async def chosen_indicator(request: Request, indicator: str = Query(...), time_before: int = Query(...),
                           time_after: int = Query(...), session: AsyncSession = Depends(get_session)):
    cur_map_name = 'map'
    folium_map = get_folium_map()
    if indicator in ['Population', 'Children']:
        indicator = indicator.lower()

    if indicator != 'Empty Map':
        try:
            data = await get_indicator(indicator, session)
        except HTTPException:
            return RedirectResponse(url="/map", status_code=status.HTTP_404_NOT_FOUND)
        colormap = add_colorbar(data, folium_map, indicator)
        for row in data:
            add_circle_marker(row, folium_map, indicator, colormap)

    cur_map_name = 'map_' + indicator
    filename = cur_map_name + '.html'
    folium_map.save(f"templates/{filename}")

    return templates.TemplateResponse(name=filename,
                                      context={"request": request})
