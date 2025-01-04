import os
import json
import yaml
import httpx

from crawlers.utils.logger import logger
from crawlers.tiktok.web.xbogus import XBogus as XB
from crawlers.utils.utils import get_timestamp

# Read the configuration file
path = os.path.abspath(os.path.dirname(__file__))

with open(f"{path}/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

class TokenManager:
    tiktok_manager = config.get("TokenManager").get("tiktok")
    token_conf = tiktok_manager.get("msToken", None)
    ttwid_conf = tiktok_manager.get("ttwid", None)
    odin_tt_conf = tiktok_manager.get("odin_tt", None)
    proxies_conf = tiktok_manager.get("proxies", None)
    proxies = {
        "http://": proxies_conf.get("http", None),
        "https://": proxies_conf.get("https", None),
    }

    @classmethod
    def gen_real_msToken(cls) -> str:
        """
        生成真实的msToken,当出现错误时返回虚假的值
        (Generate a real msToken and return a false value when an error occurs)
        """

        payload = json.dumps(
            {
                "magic": cls.token_conf["magic"],
                "version": cls.token_conf["version"],
                "dataType": cls.token_conf["dataType"],
                "strData": cls.token_conf["strData"],
                "tspFromClient": get_timestamp(),
            }
        )

        headers = {
            "User-Agent": cls.token_conf["User-Agent"],
            "Content-Type": "application/json",
        }

        transport = httpx.HTTPTransport(retries=5)
        with httpx.Client(transport=transport, proxies=cls.proxies) as client:
            try:
                response = client.post(
                    cls.token_conf["url"], headers=headers, content=payload
                )
                response.raise_for_status()

                msToken = str(httpx.Cookies(response.cookies).get("msToken"))

                return msToken

            except Exception as e:
                # 返回虚假的msToken (Return a fake msToken)
                logger.error("生成TikTok msToken API错误：{0}".format(e))
                logger.info("当前网络无法正常访问TikTok服务器，已经使用虚假msToken以继续运行。")
                logger.info("并且TikTok相关API大概率无法正常使用，请在(/tiktok/web/config.yaml)中更新代理。")
                logger.info("如果你不需要使用TikTok相关API，请忽略此消息。")
                return cls.gen_false_msToken()

class BogusManager:
    @classmethod
    def xb_str_2_endpoint(
            cls,
            user_agent: str,
            endpoint: str,
    ) -> str:
        try:
            final_endpoint = XB(user_agent).getXBogus(endpoint)
        except Exception as e:
            raise RuntimeError("生成X-Bogus失败: {0})".format(e))

        return final_endpoint[0]

    @classmethod
    def model_2_endpoint(
            cls,
            base_endpoint: str,
            params: dict,
            user_agent: str,
    ) -> str:
        # 检查params是否是一个字典 (Check if params is a dict)
        if not isinstance(params, dict):
            raise TypeError("参数必须是字典类型")

        param_str = "&".join([f"{k}={v}" for k, v in params.items()])

        try:
            xb_value = XB(user_agent).getXBogus(param_str)
        except Exception as e:
            raise RuntimeError("生成X-Bogus失败: {0})".format(e))

        # 检查base_endpoint是否已有查询参数 (Check if base_endpoint already has query parameters)
        separator = "&" if "?" in base_endpoint else "?"

        final_endpoint = f"{base_endpoint}{separator}{param_str}&X-Bogus={xb_value[1]}"

        return final_endpoint