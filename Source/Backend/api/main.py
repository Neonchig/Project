from fastapi import FastAPI
from icon import router as routeIcon
from registerUser import router as routeRegister


app = FastAPI()

app.include_router(routeIcon)
app.include_router(routeRegister)