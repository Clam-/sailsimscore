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

@view_config(route_name='create_user', renderer='../templates/create_user.jinja2')
def create_user(request):
    next_url = request.params.get('next', request.referrer)
    if (not next_url) or next_url == request.route_url('create_user'):
        next_url = request.route_url('home')
    message = ''
    item = User(name="")
    item.role = Role.user
    if 'form.submitted' in request.params:
        url=request.route_url('create_user')

        name = request.params.get('name')
        email = request.params.get('email')
        password = request.params.get('password')
        password2 = request.params.get('password2')
        if not password:
            request.session.flash("d|Require Password")
            request.dbsession.rollback()
            return dict(item=item, url=url, next_url=next_url)
        if password != password2:
            request.session.flash("d|Passwords do not match")
            request.dbsession.rollback()
            return dict(item=item, url=url, next_url=next_url)
        if not name:
            request.session.flash("d|Require Display Name")
            request.dbsession.rollback()
            return dict(item=item, url=url, next_url=next_url)
        if not email:
            request.session.flash("d|Require Email")
            request.dbsession.rollback()
            return dict(item=item, url=url, next_url=next_url)
        item.setEmail(email)
        try: request.dbsession.flush()
        except IntegrityError:
            request.session.flash("d|Email already in use")
            request.dbsession.rollback()
            return dict(item=item, url=url, next_url=next_url)
        item.setName(name)
        try: request.dbsession.flush()
        except IntegrityError:
            request.session.flash("d|Display Name in use")
            request.dbsession.rollback()
            return dict(item=item, url=url, next_url=next_url)

        item.set_password(password)
        request.dbsession.add(item)
        try: request.dbsession.flush()
        except IntegrityError:
            request.session.flash("d|Username already exists")
            request.dbsession.rollback()
            return dict(item=item, url=request.route_url('create_user'), next_url=next_url)
        headers = remember(request, item.id)
        return HTTPFound(location=next_url, headers=headers)
    return dict(item=item, url=request.route_url('create_user'), next_url=next_url)

@view_config(route_name='login', renderer='../templates/login.jinja2')
def login(request):
    next_url = request.params.get('next', request.referrer)
    if not next_url:
        next_url = request.route_url('home')
    message = ''
    login = ''
    if 'form.submitted' in request.params:
        login = request.params.get('email')
        password = request.params.get('password')
        user = request.dbsession.query(User).filter_by(email=login).first()
        if user is not None and user.check_password(password):
            headers = remember(request, user.id)
            return HTTPFound(location=next_url, headers=headers)
        message = 'Failed login'

    return dict(
        message=message,
        url=request.route_url('login'),
        next_url=next_url,
        login=login,
        )

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    next_url = request.route_url('home')
    return HTTPFound(location=next_url, headers=headers)

@forbidden_view_config()
def forbidden_view(request):
    next_url = request.route_url('login', _query={'next': request.url})
    return HTTPFound(location=next_url)
