from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import authenticate_request, AuthenticateRequestOptions
import httpx

app = FastAPI()

templates = Jinja2Templates(directory="templates")

items = []

pk = ''
sk = ''

clerk = Clerk(bearer_auth=sk)

@app.middleware('http')
def authenticate_with_clerk(request: Request, call_next):
    options = AuthenticateRequestOptions()
    httpx_request = fastapi_to_httpx_request(request)
    request_state = authenticate_request(clerk, httpx_request, options)
    print(request_state)
    response = call_next(request)
    return response

@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )

@app.get('/api/user')
def get_user(request: Request):
    return { 'user': 1 }

def fastapi_to_httpx_request(request: Request) -> httpx.Request:
    httpx_request = httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=request.headers,
    )

    return httpx_request
