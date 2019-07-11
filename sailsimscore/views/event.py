from pyramid.compat import escape
import re
import markdown

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..models import Event

@view_config(route_name='list_event', renderer='../templates/list_event.jinja2')
def list_event(request):
    items = request.dbsession.query(Event)
    return dict(items=items)

@view_config(route_name='current_event', renderer='../templates/list_event.jinja2')
def current_event(request):
    item = request.dbsession.query(Event).filter(Event.current==True).first()
    if item:
        return HTTPFound(location=request.route_url('view_event', iid=item.id))
    else:
        return HTTPFound(location=request.route_url("list_event"))

@view_config(route_name='view_event', renderer='../templates/view_event.jinja2',
             permission='view')
def view_event(request):
    item = request.context.item
    edit_url = request.route_url('edit_event', iid=item.id)
    return dict(item=item, edit_url=edit_url,
        notes=markdown.markdown(item.notes if item.notes else "", output_format="html5"))

@view_config(route_name='edit_event', renderer='../templates/edit_event.jinja2',
             permission='edit')
def edit_event(request):
    item = request.context.item
    if 'form.submitted' in request.params:
        prev = item.current
        new = 'currentCheck' in request.params
        if new and not prev:
            request.dbsession.query(Event).update({Event.current:False})
        item.name = request.params['eventName']
        item.order = request.params['orderIndex']
        item.active = 'activeCheck' in request.params
        item.current = 'currentCheck' in request.params
        item.notes = request.params['notes']
        item.modip = request.remote_addr
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
        item.user = request.user
        item.name = request.params['eventName']
        item.createdip = request.remote_addr
        request.dbsession.add(item)
        request.dbsession.flush()
        return edit_event(request)
    save_url = request.route_url('add_event')
    return dict(item=item, save_url=save_url)

@view_config(route_name='delete_event', renderer='../templates/delete_item.jinja2',
             permission='edit')
def del_event(request):
    item = request.context.item
    del_url = request.route_url('delete_event', iid=item.id)
    if 'form.submitted' in request.params:
        request.dbsession.delete(item)
        return HTTPFound(location=request.route_url('list_event'))
    return dict(item=item, del_url=del_url)
