import json
import logging

from enum import Enum
from functools import cache, cached_property
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, DirectoryPath, PositiveInt, ValidationError, field_validator
from pydantic_settings import BaseSettings


load_dotenv()  # take environment variables from .env.


BASE_DIR = Path(__file__).resolve().parent.parent


class LogLevel(str, Enum):
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class BrowserType(str, Enum):
    CHROMIUM = 'chromium'
    FIREFOX = 'firefox'
    WEBKIT = 'webkit'


class ScreenshotType(str, Enum):
    JPEG = 'jpeg'
    PNG = 'png'


class Settings(BaseSettings):
    # general settings
    host: str = Field(alias='HOST', default='0.0.0.0', description='Interface address to bind the server to')
    port: PositiveInt = Field(alias='PORT', default=3000, description='Web interface port number')
    in_docker: bool = Field(alias='IN_DOCKER', default=False)
    log_level: LogLevel = Field(alias='LOG_LEVEL', default=LogLevel.INFO, description='Logging detail level')
    basic_htpasswd: str = Field(
        alias='BASIC_HTPASSWD', default='/.htpasswd', description='Path to the htpasswd file for basic authentication'
    )

    # browser settings
    browser_type: BrowserType = Field(
        alias='BROWSER_TYPE',
        default=BrowserType.CHROMIUM,
        description='Browser type to use (chromium, firefox, webkit)',
    )
    browser_context_limit: PositiveInt = Field(
        alias='BROWSER_CONTEXT_LIMIT', default=20, description='Maximum number of browser contexts (aka tabs)'
    )
    screenshot_type: ScreenshotType = Field(
        alias='SCREENSHOT_TYPE', default=ScreenshotType.JPEG, description='Screenshot type (jpeg or png)'
    )
    screenshot_quality: PositiveInt = Field(
        alias='SCREENSHOT_QUALITY', default=80, description='Screenshot quality (0-100)', ge=0, le=100
    )

    # path settings
    user_data_dir: DirectoryPath = Field(
        alias='USER_DATA_DIR',
        default=BASE_DIR / 'user_data',
        description='This directory contains browser session data such as cookies and local storage',
    )
    user_scripts_dir: DirectoryPath = Field(
        alias='USER_SCRIPTS_DIR',
        default=BASE_DIR / 'user_scripts',
        description='In this directory, you can place your own JavaScript scripts, which you can then embed on pages through the Scrapper API',
    )
    app_dir: DirectoryPath = Field(
        alias='APP_DIR',
        default=BASE_DIR / 'app',
        description='This directory contains the application files, including templates and static files',
    )

    # ssl settings
    ssl_keyfile: str = Field(alias='SSL_KEYFILE', default='/.ssl/key.pem')
    ssl_keyfile_password: str | None = Field(alias='SSL_KEYFILE_PASSWORD', default=None)
    ssl_certfile: str = Field(alias='SSL_CERTFILE', default='/.ssl/cert.pem')
    ssl_ciphers: str = Field(alias='SSL_CIPHERS', default='TLSv1')

    # uvicorn settings
    workers: PositiveInt = Field(
        alias='UVICORN_WORKERS', default=1, description='Number of web server worker processes'
    )
    debug: bool = Field(alias='DEBUG', default=False, description='Enable debug mode')

    # version settings
    git_tag: str = Field(alias='GIT_TAG', default='v0.0.0')
    git_sha: str = Field(alias='GIT_SHA', default='')

    @field_validator('log_level', mode='before')
    def lowercase_log_level(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

    @cached_property
    def log_level_num(self) -> int:
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }
        return level_map[self.log_level]


try:
    _settings = Settings()
except ValidationError as err:
    raise SystemExit(err) from err


VERSION = _settings.git_tag
REVISION = f'{_settings.git_tag}-{_settings.git_sha[:7]}'

# general settings
HOST = _settings.host
PORT = _settings.port
IN_DOCKER = _settings.in_docker
LOG_LEVEL = _settings.log_level_num
BASIC_HTPASSWD = _settings.basic_htpasswd
AUTH_ENABLED = Path(BASIC_HTPASSWD).exists()

# browser settings
BROWSER_TYPE = _settings.browser_type
BROWSER_CONTEXT_LIMIT = _settings.browser_context_limit
SCREENSHOT_TYPE = _settings.screenshot_type
SCREENSHOT_QUALITY = _settings.screenshot_quality

# path settings
USER_DATA_DIR = _settings.user_data_dir
USER_SCRIPTS_DIR = _settings.user_scripts_dir
APP_DIR = _settings.app_dir
# calculated paths
TEMPLATES_DIR = APP_DIR / 'templates'
STATIC_DIR = APP_DIR / 'static'
SCRIPTS_DIR = APP_DIR / 'scripts'
READABILITY_SCRIPT = SCRIPTS_DIR / 'readability' / '0.6.0' / 'Readability.js'  # commit hash
PARSER_SCRIPTS_DIR = SCRIPTS_DIR / 'parser'
ICON_PATH = STATIC_DIR / 'icons' / 'favicon.ico'

# ssl settings
SSL_KEYFILE = _settings.ssl_keyfile
SSL_KEYFILE_PASSWORD = _settings.ssl_keyfile_password
SSL_CERTFILE = _settings.ssl_certfile
SSL_CIPHERS = _settings.ssl_ciphers

# uvicorn settings
WORKERS = _settings.workers
DEBUG = _settings.debug


# other settings
@cache
def load_device_registry():
    # https://playwright.dev/python/docs/emulation#devices
    # https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/deviceDescriptorsSource.json
    path = APP_DIR / 'internal' / 'deviceDescriptorsSource.json'
    with open(path, encoding='utf-8') as f:
        return json.load(f)


DEVICE_REGISTRY = load_device_registry()


def to_string() -> str:
    """Return a formatted string with all settings for logging purposes."""
    settings_dict = _settings.model_dump()
    # Hide sensitive information
    if _settings.ssl_keyfile_password:
        settings_dict['ssl_keyfile_password'] = '********'

    lines = []
    lines.append('Scrapper settings:')

    # Group settings by categories for better readability
    categories = {
        'General settings': [
            'host',
            'port',
            'in_docker',
            'log_level',
            'basic_htpasswd',
        ],
        'Browser settings': [
            'browser_type',
            'browser_context_limit',
            'screenshot_type',
            'screenshot_quality',
        ],
        'Path settings': [
            'user_data_dir',
            'user_scripts_dir',
            'app_dir',
        ],
        'SSL settings': ['ssl_keyfile', 'ssl_keyfile_password', 'ssl_certfile', 'ssl_ciphers'],
        'Uvicorn settings': ['workers', 'debug'],
        'Version info': ['git_tag', 'git_sha'],
    }

    for category, keys in categories.items():
        lines.append(f'\n{category}:')
        for key in keys:
            if key in settings_dict:
                lines.append(f'  {key}: {settings_dict[key]}')

    return '\n'.join(lines)
