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

from ..models import User
from ..models.user import Role


@view_config(route_name='edit_user', renderer='../templates/my_account.jinja2',
             permission='edit')
def edit_user(request):
    item = request.context.item
    edit_url = request.route_url('edit_user', iid=item.id)
    if 'form.submitted' in request.params:
        name = request.params.get('name')
        email = request.params.get('email')
        if not name:
            request.session.flash("d|Require Display Name")
            request.dbsession.rollback()
            return dict(item=item, url=edit_url)
        if not email:
            request.session.flash("d|Require Email")
            request.dbsession.rollback()
            return dict(item=item, url=edit_url)
        item.setEmail(email)
        try: request.dbsession.flush()
        except IntegrityError:
            request.session.flash("d|Email in use")
            request.dbsession.rollback()
            return dict(item=item, url=edit_url, next_url=next_url)
        item.setName(name)
        try: request.dbsession.flush()
        except IntegrityError:
            request.session.flash("d|Display Name in use")
            request.dbsession.rollback()
            return dict(item=item, url=edit_url, next_url=next_url)
        item.set_password(request.params.get('password'))
        return HTTPFound(location=request.route_url('view_user', iid=item.id))
    return dict(item=item, url=edit_url)

@view_config(route_name='view_user', renderer='../templates/my_account.jinja2',
             permission='edit')
def view_user(request):
    item = request.context.item
    edit_url = request.route_url('edit_user', iid=item.id)
    return dict(item=item, url=edit_url)
