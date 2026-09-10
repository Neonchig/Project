from fastapi import FastAPI
from icon import router as routeIcon
from registerUser import router as routeRegister
from loginUser import router as loginRoute


app = FastAPI()

app.include_router(routeIcon)
app.include_router(routeRegister)
app.include_router(loginRoute)