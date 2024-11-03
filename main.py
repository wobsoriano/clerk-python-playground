import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
import httpx

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

clerk_publishable_key=os.getenv('CLERK_PUBLISHABLE_KEY')
clerk_secret_key=os.getenv('CLERK_SECRET_KEY')

clerk = Clerk(bearer_auth=clerk_secret_key)

@app.middleware('http')
async def authenticate_with_clerk(request: Request, call_next):
    options = AuthenticateRequestOptions()
    httpx_request = fastapi_to_httpx_request(request)
    request_state = clerk.authenticate_request(httpx_request, options)
    request.state.user_id = None if request_state.payload is None else request_state.payload['sub']
    response = await call_next(request)
    return response

@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={'user_id': request.state.user_id, 'clerk_publishable_key': clerk_publishable_key}
    )

@app.get('/api/get_user')
def get_user(request: Request):
    # https://github.com/clerk/clerk-sdk-python/issues/36
    # user = clerk.users.get(request.state.user_id)
    return { 'user': 1 }

def fastapi_to_httpx_request(request: Request):
    print(request.url)
    httpx_request = httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=request.headers,
    )

    return httpx_request
