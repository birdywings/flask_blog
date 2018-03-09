from flask import Blueprint


main = Blueprint('main',__name__) #登记main蓝本

from . import errors,views
from ..models import Permission

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
