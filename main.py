from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from clerk_backend_api.jwks_helpers import authenticate_request, Clerk, AuthenticateRequestOptions

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

items = []

pk = ''
sk = ''

clerk = Clerk()

print(authenticate_request)

@app.middleware('http')
async def authenticate_with_clerk(request: Request, call_next):
    options = AuthenticateRequestOptions(
        secret_key=sk
    )
    x = authenticate_request(clerk, request, options)
    print(x)
    response = await call_next(request)
    return response

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )

@app.post('/items')
def create_item(item: str):
    items.append(item)
    return items
