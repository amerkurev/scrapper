import os
import hashlib
import json

from pathlib import Path
from typing import Any

from settings import USER_DATA_DIR, SCREENSHOT_TYPE


def make_key(s: Any) -> str:
    return hashlib.sha1(str(s).encode()).hexdigest()


def dump_result(data: Any, key: str, screenshot: bytes | None = None) -> None:
    path = json_location(key)

    # create dir if not exists
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

    # save result as json
    with open(path, mode='w') as f:
        json.dump(data, f, ensure_ascii=True)

    # save screenshot
    if screenshot:
        with open(screenshot_location(key), mode='wb') as f:
            f.write(screenshot)


def load_result(key: str) -> Any | None:
    path = json_location(key)
    if not path.exists():
        return None
    with open(path, mode='r') as f:
        return json.load(f)


def json_location(filename: str) -> Path:
    return USER_DATA_DIR / '_res' / filename[:2] / filename


def screenshot_location(filename: str) -> Path:
    return USER_DATA_DIR / '_res' / filename[:2] / (filename + '.' + SCREENSHOT_TYPE)
