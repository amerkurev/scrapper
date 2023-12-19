import os
from pathlib import Path


IN_DOCKER = os.environ.get('IN_DOCKER')
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USER_DATA_DIR = Path(os.environ.get('USER_DATA_DIR', BASE_DIR / 'user_data_dir'))
USER_SCRIPTS = Path(os.environ.get('USER_SCRIPTS', BASE_DIR / 'user_scripts'))
APP_DIR = Path(os.environ.get('APP_DIR', BASE_DIR / 'app'))
TEMPLATES_DIR = APP_DIR / 'templates'
STATIC_DIR = APP_DIR / 'static'
SCRIPTS_DIR = APP_DIR / 'scripts'
READABILITY_SCRIPT = SCRIPTS_DIR / 'readability' / '0.5.0' / 'Readability.js'  # commit hash
PARSER_SCRIPTS_DIR = SCRIPTS_DIR / 'parser'
STEALTH_SCRIPTS_DIR = SCRIPTS_DIR / 'stealth'
SCREENSHOT_TYPE = 'jpeg'  # png, jpeg
SCREENSHOT_QUALITY = 80  # 0-100
ICON_PATH = STATIC_DIR / 'icons' / 'favicon.ico'
