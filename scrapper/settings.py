
import os
from pathlib import Path


IN_DOCKER = os.environ.get('IN_DOCKER')
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
USER_DATA_DIR = Path(os.environ.get('USER_DATA_DIR', BASE_DIR / 'user_data_dir'))
USER_SCRIPTS = Path(os.environ.get('USER_SCRIPTS', BASE_DIR / 'user_scripts'))
APP_HOME = BASE_DIR / 'scrapper'
STATIC_DIR = APP_HOME / 'static'
SCRIPTS_DIR = APP_HOME / 'scripts'
READABILITY_SCRIPT = SCRIPTS_DIR / 'readability' / '8e8ec27' / 'Readability.js'  # commit hash
PARSER_SCRIPTS_DIR = SCRIPTS_DIR / 'parser'
STEALTH_SCRIPTS_DIR = SCRIPTS_DIR / 'stealth'
SCREENSHOT_TYPE = 'jpeg'  # png, jpeg
SCREENSHOT_QUALITY = 80  # 0-100
