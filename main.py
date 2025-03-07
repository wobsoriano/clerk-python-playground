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

sdk = Clerk(bearer_auth=clerk_secret_key)

def fastapi_to_httpx_request(request: Request) -> httpx.Request:
    return httpx.Request(
        method=request.method,
        url=str(request.url),
        headers=request.headers,
    )

@app.middleware('http')
async def authenticate_with_clerk(request: Request, call_next):
    options = AuthenticateRequestOptions(
        secret_key=clerk_secret_key
    )
    
    httpx_request = fastapi_to_httpx_request(request)
    request_state = sdk.authenticate_request(httpx_request, options)
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
    user = sdk.users.get(user_id=request.state.user_id)
    return { 'user': user }