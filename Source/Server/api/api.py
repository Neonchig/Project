import uvicorn
from fastapi import FastAPI

from Source.Server.api.icon import router as routeIcon
from Source.Server.api.login_user import router as loginRoute
from Source.Server.api.refresh import router as routeRefresh
from Source.Server.api.register_user import router as routeRegister

app = FastAPI()

app.include_router(routeIcon)
app.include_router(routeRegister)
app.include_router(loginRoute)
app.include_router(routeRefresh)

async def api_serve():

    config = uvicorn.Config(
        app = app,
        host = "0.0.0.0",
        port = 8080
    )

    server = uvicorn.Server(config)
    await server.serve()
