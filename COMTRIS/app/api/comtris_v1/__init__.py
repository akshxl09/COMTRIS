'''
COMTRIS V1 API Module Package
'''
from flask import Blueprint

comtris_v1 = Blueprint('comtris_v1', __name__)

from . import *
