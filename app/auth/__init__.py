from flask import Blueprint

auth = Blueprint('auth',__name__) #登记auth蓝本

from . import views

