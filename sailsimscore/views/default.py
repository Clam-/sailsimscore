from pyramid.compat import escape
import re

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from .. import models

@view_config(route_name='home')
def view_home(request):
    # Get default event, if no default, go to list
    next_url = request.route_url('list_event')
    return HTTPFound(location=next_url)
