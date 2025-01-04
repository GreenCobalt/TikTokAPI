import yaml
import os

from crawlers.base_crawler import BaseCrawler
from crawlers.tiktok.web.endpoints import TikTokAPIEndpoints

from crawlers.tiktok.web.utils import BogusManager
from crawlers.tiktok.web.models import PostDetail

path = os.path.abspath(os.path.dirname(__file__))
with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

class TikTokWebCrawler:
    def __init__(self):
        self.proxy_pool = None

    async def get_tiktok_headers(self):
        tiktok_config = config["TokenManager"]["tiktok"]
        kwargs = {
            "headers": {
                "User-Agent": tiktok_config["headers"]["User-Agent"],
                "Referer": tiktok_config["headers"]["Referer"],
                "Cookie": tiktok_config["headers"]["Cookie"],
            },
            "proxies": { "http://": None, "https://": None }
        }
        return kwargs
    
    async def fetch_one_video(self, itemId: str):
        kwargs = await self.get_tiktok_headers()

        base_crawler = BaseCrawler(proxies=kwargs["proxies"], crawler_headers=kwargs["headers"])
        async with base_crawler as crawler:
            params = PostDetail(itemId=itemId)
            endpoint = BogusManager.model_2_endpoint(
                TikTokAPIEndpoints.POST_DETAIL, params.dict(), kwargs["headers"]["User-Agent"]
            )
            response = await crawler.fetch_get_json(endpoint)
        return response