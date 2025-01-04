from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Optional, Dict

app = FastAPI()

class ResponseModel(BaseModel):
    data: Optional[Any] = {}

class ErrorResponseModel(BaseModel):
    code: int = 400
    router: str
    params: dict = {}