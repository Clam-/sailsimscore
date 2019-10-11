from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    )
from pyramid.view import (
    forbidden_view_config,
    view_config,
)
from sqlalchemy.exc import IntegrityError

from ..models import Boat

@view_config(route_name='list_boat', renderer='../templates/list_boat.jinja2')
def list_boat(request):
    items = request.dbsession.query(Boat)
    return dict(items=items)

@view_config(route_name='edit_boat', renderer='../templates/edit_boat.jinja2',
             permission='edit')
def edit_boat(request):
    item = request.context.item
    if item.id:
        edit_url = request.route_url("edit_boat", iid=item.id)
    else:
        edit_url = request.route_url("add_boat")
    if 'form.submitted' in request.params:
        item.name = request.params.get('boat_name')
        item.resource = request.params.get('boat_res')
        if not item.name:
            request.session.flash("d|Require name")
            request.dbsession.rollback()
            return dict(item=item, url=edit_url)
        return HTTPFound(location=request.route_url('view_boat', iid=item.id))
    return dict(item=item, url=edit_url)

@view_config(route_name='add_boat', renderer='../templates/edit_boat.jinja2',
             permission='create')
def add_boat(request):
    item = request.context.item
    save_url = request.route_url('add_boat')
    if 'form.submitted' in request.params:
        bid = None
        try:
            bid = int(request.params.get('boat_id'))
        except ValueError:
            request.session.flash("d|Require numerical ID")
            request.dbsession.rollback()
            return dict(item=item, url=save_url)
        if not bid:
            request.session.flash("d|Require numerical ID")
            request.dbsession.rollback()
            return dict(item=item, url=save_url)
        request.dbsession.add(item)
        try: request.dbsession.flush()
        except IntegrityError:
            request.dbsession.rollback()
            request.session.flash("d|ID already exists")
            return dict(item=item, url=save_url)
        return edit_boat(request)
    return dict(item=item, save_url=save_url)

@view_config(route_name='view_boat', renderer='../templates/view_boat.jinja2',
             permission='view')
def view_boat(request):
    item = request.context.item
    edit_url = request.route_url('edit_boat', iid=item.id)
    return dict(item=item, url=edit_url)
