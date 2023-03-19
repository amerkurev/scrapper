
import os
import json

from scrapper.settings import USER_DATA_DIR, SCREENSHOT_TYPE


def dump_result(data, filename, screenshot=None):
    path = json_location(filename)

    # create dir if not exists
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

    # save result as json
    with open(path, mode='w') as f:
        json.dump(data, f, ensure_ascii=True)

    # save screenshot
    if screenshot:
        with open(screenshot_location(filename), mode='wb') as f:
            f.write(screenshot)


def load_result(filename):
    path = json_location(filename)
    if not path.exists():
        return None
    with open(path, mode='r') as f:
        return json.load(f)


def json_location(filename):
    return USER_DATA_DIR / '_res' / filename[:2] / filename


def screenshot_location(filename):
    return str(json_location(filename)) + '.' + SCREENSHOT_TYPE
