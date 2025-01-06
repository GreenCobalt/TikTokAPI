import uvicorn
from fastapi import FastAPI
from app.api.router import router as api_router
import os

Host_IP = "0.0.0.0"
Host_Port = 9000

app = FastAPI(title="TikTok API")

# API router
app.include_router(api_router, prefix="")

if __name__ == '__main__':
    uvicorn.run(app, host=Host_IP, port=Host_Port)