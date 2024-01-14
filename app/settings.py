import json
import os
from functools import cache
from pathlib import Path


BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USER_DATA_DIR = Path(os.environ.get('USER_DATA_DIR', BASE_DIR / 'user_data'))
USER_SCRIPTS_DIR = Path(os.environ.get('USER_SCRIPTS_DIR', BASE_DIR / 'user_scripts'))
APP_DIR = Path(os.environ.get('APP_DIR', BASE_DIR / 'app'))
TEMPLATES_DIR = APP_DIR / 'templates'
STATIC_DIR = APP_DIR / 'static'
SCRIPTS_DIR = APP_DIR / 'scripts'
READABILITY_SCRIPT = SCRIPTS_DIR / 'readability' / '0.5.0' / 'Readability.js'  # commit hash
PARSER_SCRIPTS_DIR = SCRIPTS_DIR / 'parser'
STEALTH_SCRIPTS_DIR = SCRIPTS_DIR / 'stealth'
ICON_PATH = STATIC_DIR / 'icons' / 'favicon.ico'

BROWSER_CONTEXT_LIMIT = int(os.environ.get('BROWSER_CONTEXT_LIMIT', 20))
SCREENSHOT_TYPE = os.environ.get('SCREENSHOT_TYPE', 'jpeg')  # jpeg, png
SCREENSHOT_QUALITY = int(os.environ.get('SCREENSHOT_QUALITY', 80))  # 0-100

assert BROWSER_CONTEXT_LIMIT > 0, 'BROWSER_CONTEXT_LIMIT must be greater than 0'
assert SCREENSHOT_TYPE in ('jpeg', 'png'), 'SCREENSHOT_TYPE must be jpeg or png'
assert 0 <= SCREENSHOT_QUALITY <= 100, 'SCREENSHOT_QUALITY must be between 0 and 100'


@cache
def load_device_registry():
    # https://playwright.dev/python/docs/emulation#devices
    # https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/deviceDescriptorsSource.json
    src_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'internal', 'deviceDescriptorsSource.json')
    with open(src_file, encoding='utf-8') as f:
        return json.load(f)


DEVICE_REGISTRY = load_device_registry()
