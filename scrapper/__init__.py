
from flask import Flask
from scrapper.settings import STATIC_DIR

app = Flask(__name__, static_folder=STATIC_DIR)

from scrapper.views import startup
startup()
