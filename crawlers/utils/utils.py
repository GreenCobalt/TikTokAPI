import re
import sys
import random
import secrets
import datetime

from typing import Union, List

seed_bytes = secrets.token_bytes(16)
seed_int = int.from_bytes(seed_bytes, "big")
random.seed(seed_int)

def gen_random_str(randomlength: int) -> str:
    base_str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-"
    return "".join(random.choice(base_str) for _ in range(randomlength))

def get_timestamp(unit: str = "milli"):
    now = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    if unit == "milli":
        return int(now.total_seconds() * 1000)
    elif unit == "sec":
        return int(now.total_seconds())
    elif unit == "min":
        return int(now.total_seconds() / 60)
    else:
        raise ValueError("Unsupported time unit")

def extract_valid_urls(inputs: Union[str, List[str]]) -> Union[str, List[str], None]:
    url_pattern = re.compile(r"https?://\S+")

    if isinstance(inputs, str):
        match = url_pattern.search(inputs)
        return match.group(0) if match else None
    elif isinstance(inputs, list):
        valid_urls = []

        for input_str in inputs:
            matches = url_pattern.findall(input_str)
            if matches:
                valid_urls.extend(matches)

        return valid_urls

def split_filename(text: str, os_limit: dict) -> str:
    os_name = sys.platform
    filename_length_limit = os_limit.get(os_name, 200)

    english_length = sum(1 for char in text if char.isalpha())
    num_underscores = text.count("_")
    total_length = english_length + num_underscores

    if total_length > filename_length_limit:
        split_index = min(total_length, filename_length_limit) // 2 - 6
        split_text = text[:split_index] + "......" + text[-split_index:]
        return split_text
    else:
        return text