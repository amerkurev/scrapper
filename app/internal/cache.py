import os
import hashlib
import json

from pathlib import Path
from typing import Any, Union

from google.cloud import storage

from settings import USER_DATA_DIR, SCREENSHOT_TYPE, ENV, GCS_BUCKET_NAME

def make_key(s: Any) -> str:
    return hashlib.sha1(str(s).encode()).hexdigest()

def dump_result(data: Any, key: str, screenshot: bytes | None = None) -> None:
    if ENV == 'production':
        _dump_result_gcs(data, key, screenshot)
    else:
        _dump_result_local(data, key, screenshot)

def _dump_result_local(data: Any, key: str, screenshot: bytes | None = None) -> None:
    path = json_local_location(key)

    # create dir if not exists
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

    # save result as json
    with open(path, mode='w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=True)

    # save screenshot
    if screenshot:
        with open(screenshot_local_location(key), mode='wb') as f:
            f.write(screenshot)

def _dump_result_gcs(data: Any, key: str, screenshot: bytes | None = None) -> None:
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    json_blob = bucket.blob(f'_res/{key[:2]}/{key}')
    json_blob.upload_from_string(json.dumps(data, ensure_ascii=True), content_type='application/json')

    if screenshot:
        screenshot_blob = bucket.blob(f'_res/{key[:2]}/{key}.{SCREENSHOT_TYPE}')
        screenshot_blob.upload_from_string(screenshot, content_type=f'image/{SCREENSHOT_TYPE}')

def load_result(key: str) -> Any | None:
    if ENV == 'production':
        return _load_result_gcs(key)

    return _load_result_local(key)

def _load_result_local(key: str) -> Any | None:
    path = json_local_location(key)
    if not path.exists():
        return None
    with open(path, mode='r', encoding='utf-8') as f:
        return json.load(f)

def _load_result_gcs(key: str) -> Any | None:
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f'_res/{key[:2]}/{key}')
    if not blob.exists():
        return None

    return json.loads(blob.download_as_string())

def json_local_location(key: str) -> Union[Path, str]:
    return USER_DATA_DIR / '_res' / key[:2] / key

def screenshot_local_location(key: str) -> Union[Path, str]:
    return USER_DATA_DIR / '_res' / key[:2] / (key + '.' + SCREENSHOT_TYPE)

def load_screenshot(key: str) -> bytes | None:
    if ENV == 'production':
        return _load_screenshot_gcs(key)

    return _load_screenshot_local(key)

def _load_screenshot_local(key: str) -> bytes | None:
    path = screenshot_local_location(key)
    if not path.exists():
        return None
    with open(path, mode='rb') as f:
        return f.read()

def _load_screenshot_gcs(key: str) -> bytes | None:
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f'_res/{key[:2]}/{key}.{SCREENSHOT_TYPE}')
    if not blob.exists():
        return None

    return blob.download_as_bytes()
