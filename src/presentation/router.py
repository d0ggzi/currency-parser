import logging

from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.adapter.parsers import ParserAdapter

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory='templates')


async def validation_exception_handler(request: Request, exc: HTTPException) -> templates.TemplateResponse:
    url = request.url.path
    logger.info("Ошибка валидации данных по url %s", url)
    if url == "/chart":
        parser_adapter = ParserAdapter()
        countries = parser_adapter.get_all_countries()
        return templates.TemplateResponse('index.html', {'request': request, 'countries': countries,
                                                         'error': "Некорректный запрос"})
    elif url == "/parser":
        return templates.TemplateResponse('parser.html', {'request': request,
                                                          'error': "Некорректный запрос"})


@router.post('/parser', response_class=HTMLResponse)
async def parse(request: Request, start_date: str = Form(), end_date: str = Form()):
    try:
        parser_adapter = ParserAdapter()
        parser_adapter.parse(start_date=start_date, end_date=end_date)
        logger.info("Спаршены данные с %s по %s", start_date, end_date)

        return templates.TemplateResponse('parser.html',
                                          {'request': request, 'success': 'Данные были спарсены успешно'})
    except ValueError as e:
        logger.info("Ошибка парсинга данных с %s по %s", start_date, end_date)
        return templates.TemplateResponse('parser.html', {'request': request, 'error': str(e)})


@router.get('/parser', response_class=HTMLResponse)
async def parser_page(request: Request):
    return templates.TemplateResponse('parser.html', {'request': request})


@router.post('/chart', response_class=HTMLResponse)
async def chart(request: Request, start_date: str = Form(), end_date: str = Form()):
    form_data = await request.form()
    input_countries = form_data.getlist('input_country')

    parser_adapter = ParserAdapter()
    countries = parser_adapter.get_all_countries()
    try:
        data = parser_adapter.get_data_values(input_countries, start_date, end_date)
    except ValueError as e:
        logger.info("Ошибка построения графика для данных с %s по %s", start_date, end_date)
        return templates.TemplateResponse('index.html', {'request': request, 'countries': countries, 'error': str(e)})

    logger.info("График успешно построен для данных с %s по %s", start_date, end_date)
    return templates.TemplateResponse('index.html',
                                      {'request': request,
                                       'countries': countries,
                                       'data': data})


@router.get('/', response_class=HTMLResponse)
async def main(request: Request):
    parser_adapter = ParserAdapter()
    countries = parser_adapter.get_all_countries()
    return templates.TemplateResponse('index.html',
                                      {'request': request,
                                       'countries': countries})
