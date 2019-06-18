from pyramid.compat import escape
import re

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..models import Event

@view_config(route_name='list_event', renderer='../templates/list_event.jinja2')
def list_event(request):
    items = request.dbsession.query(Event)
    return dict(items=items)


@view_config(route_name='view_event', renderer='../templates/view_event.jinja2',
             permission='view')
def view_event(request):
    item = request.context.item

    edit_url = request.route_url('edit_event', iid=item.id)
    return dict(item=item, edit_url=edit_url)

@view_config(route_name='edit_event', renderer='../templates/edit_event.jinja2',
             permission='edit')
def edit_event(request):
    item = request.context.item
    if 'form.submitted' in request.params:
        item.name = request.params['eventName']
        item.order = request.params['orderIndex']
        item.active = 'activeCheck' in request.params
        item.current = 'currentCheck' in request.params
        next_url = request.route_url('view_event', iid=item.id)
        return HTTPFound(location=next_url)
    return dict(
        item=item,
        save_url=request.route_url('edit_event', iid=item.id),
        )

@view_config(route_name='add_event', renderer='../templates/edit_event.jinja2',
             permission='create')
def add_event(request):
    item = request.context.item
    if 'form.submitted' in request.params:
        item.name = request.params['eventName']
        item.order = request.params['orderIndex']
        item.active = 'activeCheck' in request.params
        item.current = 'currentCheck' in request.params
        item.user_id = request.user
        request.dbsession.add(item)
        request.dbsession.flush()
        next_url = request.route_url('view_event', iid=item.id)
        return HTTPFound(location=next_url)
    save_url = request.route_url('add_event')
    return dict(item=item, save_url=save_url)
