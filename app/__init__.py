import os
from flask import Flask
# from config import Config

app = Flask(__name__, template_folder='../templates', static_folder='../static')
# app.config.from_object(Config)

from app import routes