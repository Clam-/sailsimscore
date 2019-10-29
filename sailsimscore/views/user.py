from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import (
    remember,
    forget,
    )
from pyramid.view import (
    forbidden_view_config,
    view_config,
)
from sqlalchemy.exc import IntegrityError

from ..models import User
from ..models.user import Role

from .auth import modifyUser

@view_config(route_name='list_users', renderer='../templates/list_user.jinja2')
def list_users(request):
    items = request.dbsession.query(User)
    return dict(items=items)

@view_config(route_name='edit_user', renderer='../templates/my_account.jinja2',
             permission='edit')
def edit_user(request):
    item = request.context.item
    edit_url = request.route_url('edit_user', iid=item.id)
    name = item.name
    email = item.email
    if 'form.submitted' in request.params:
        name = request.params.get('name')
        email = request.params.get('email')
        password = request.params.get('password')
        password2 = request.params.get('password2')
        if modifyUser(request, item, name, email, password, password2, edit=True) is False:
            return dict(name=name, email=email, url=url, next_url=next_url)
        request.session.flash("s|Account updated.")
        return HTTPFound(location=request.route_url('list_users'))
    return dict(name=name, email=email, url=edit_url)

@view_config(route_name='my_account', renderer='../templates/my_account.jinja2',
             permission='account')
def my_account(request):
    item = request.user
    if not item:
        raise HTTPNotFound()
    edit_url = request.route_url('my_account')
    name = item.name
    email = item.email
    if 'form.submitted' in request.params:
        name = request.params.get('name')
        email = request.params.get('email')
        password = request.params.get('password')
        password2 = request.params.get('password2')
        if modifyUser(request, item, name, email, password, password2, edit=True) is False:
            return dict(name=name, email=email)
        request.session.flash("s|Account updated.")
        return HTTPFound(location=request.route_url('my_account'))
    return dict(name=name, email=email, url=edit_url)
