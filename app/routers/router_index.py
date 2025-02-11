from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

router = APIRouter(
    prefix="",
    tags=["Index"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_class=PlainTextResponse)
async def index():
    return "Welcome to the Crystal Logic API"

@router.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def robots():
    data = "User-agent: *\nDisallow: /"
    return PlainTextResponse(content=data)

@router.get("/client")
def read_root(request: Request):
    client_host = request.client.host
    return {"client_host": client_host}