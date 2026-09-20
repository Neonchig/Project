import uvicorn
from fastapi import FastAPI

from Source.Backend.api.icon import router as routeIcon
from Source.Backend.api.login_user import router as loginRoute
from Source.Backend.api.register_user import router as routeRegister

app = FastAPI()

app.include_router(routeIcon)
app.include_router(routeRegister)
app.include_router(loginRoute)

async def api_serve():

    config = uvicorn.Config(
        app = app,
        host = "localhost",
        port = 8080
    )

    server = uvicorn.Server(config)
    await server.serve()
