from fastapi import APIRouter, Request, HTTPException
from app.api.APIResponseModel import ResponseModel, ErrorResponseModel
from crawlers.tiktok.web.web_crawler import TikTokWebCrawler

router = APIRouter()
TikTokWebCrawler = TikTokWebCrawler()

@router.get("/video", response_model=ResponseModel)
async def video(request: Request, itemId: str):
    try:
        data = await TikTokWebCrawler.fetch_one_video(itemId)
        return ResponseModel(code=200, router=request.url.path, data=data)
    except Exception as e:
        status_code = 400
        detail = ErrorResponseModel(code=status_code, router=request.url.path, params=dict(request.query_params))
        raise HTTPException(status_code=status_code, detail=detail.dict())