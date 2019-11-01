from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    )
from pyramid.view import (
    forbidden_view_config,
    view_config,
)
from pyramid_mailer.message import Message

from sqlalchemy.exc import IntegrityError

from jwcrypto.jwe import JWE, InvalidJWEData
from jwcrypto.jwk import JWK
from jwcrypto.common import json_encode
from json import loads, dumps
from calendar import timegm
from time import gmtime
from binascii import unhexlify, hexlify

from ..models import User
from ..models.user import Role

def modifyUser(request, item, name, email, password, password2, edit=False, passwordonly=False):
    if not edit and not password:
        request.session.flash("d|Require Password")
        request.dbsession.rollback()
        return False
    if password != password2:
        request.session.flash("d|Passwords do not match")
        request.dbsession.rollback()
        return False
    if not passwordonly:
        if not name:
            request.session.flash("d|Require Display Name")
            request.dbsession.rollback()
            return False
        if not email:
            request.session.flash("d|Require Email")
            request.dbsession.rollback()
            return False
        item.email = email
        try: request.dbsession.flush()
        except IntegrityError:
            request.session.flash("d|Email already in use")
            request.dbsession.rollback()
            return False
        item.name = name
        try: request.dbsession.flush()
        except IntegrityError:
            request.session.flash("d|Display Name in use")
            request.dbsession.rollback()
            return False
    if password: item.set_password(password)
    return True

@view_config(route_name='create_user', renderer='../templates/create_user.jinja2')
def create_user(request):
    if request.user:
        # already logged in, redirect to home
        return HTTPFound(location=request.route_url('home'))
    next_url = request.params.get('next', request.referrer)
    if (not next_url) or next_url == request.route_url('create_user'):
        next_url = request.route_url('home')
    name = ''
    email = ''
    item = User(name="")
    item.role = Role.user
    if 'form.submitted' in request.params:
        url=request.route_url('create_user')
        name = request.params.get('name')
        email = request.params.get('email')
        password = request.params.get('password')
        password2 = request.params.get('password2')
        request.dbsession.add(item)
        if modifyUser(request, item, name, email, password, password2) is False:
            return dict(name=name, email=email, url=url, next_url=next_url)
        request.session.flash("s|Account created.")
        headers = remember(request, item.id)
        return HTTPFound(location=next_url, headers=headers)
    return dict(name=name, email=email, url=request.route_url('create_user'), next_url=next_url)

@view_config(route_name='login', renderer='../templates/login.jinja2')
def login(request):
    if request.user:
        # already logged in, redirect to home
        return HTTPFound(location=request.route_url('home'))
    next_url = request.params.get('next', request.referrer)
    if not next_url:
        next_url = request.route_url('home')
    login = ''
    if 'form.submitted' in request.params:
        login = request.params.get('email')
        if login: login = login.lower()
        password = request.params.get('password')
        user = request.dbsession.query(User).filter_by(email=login).first()
        if user is not None and user.check_password(password):
            headers = remember(request, user.id)
            return HTTPFound(location=next_url, headers=headers)
        request.session.flash("d|Failed login")

    return dict(
        url=request.route_url('login'),
        next_url=next_url,
        login=login,
        )

@view_config(route_name='resetpass', renderer='../templates/resetpass.jinja2')
def resetpass(request):
    if request.user:
        # already logged in, redirect to home
        return HTTPFound(location=request.route_url('home'))
    jwe = request.matchdict.get('jwe')
    if not jwe:
        request.session.flash("d|Invalid link.")
        raise HTTPFound(location=request.route_url('forgotpass'))
    # decode
    key = JWK(**loads(request.registry.settings["jwt.secret"]))
    jwetoken = JWE()
    try:
        jwetoken.deserialize(jwe)
        jwetoken.decrypt(key)
    except InvalidJWEData:
        request.session.flash("d|Invalid link?")
        raise HTTPFound(location=request.route_url('forgotpass'))
    payload = loads(jwetoken.payload)
    # check timestamp.
    nowdt = timegm(gmtime())
    if (nowdt - payload["dt"]) > (int(request.registry.settings["jwt.expire"])*60):
        request.session.flash("d|Link has expired.")
        raise HTTPFound(location=request.route_url('forgotpass'))
    # load user...
    item = request.dbsession.query(User).filter_by(id=payload["id"]).first()
    if not item:
        request.session.flash("d|User not found.")
        raise HTTPFound(location=request.route_url('forgotpass'))
    # check if password already changed:
    if item.password_hash != unhexlify(payload["hash"]):
        request.session.flash("d|Link has expired..")
        raise HTTPFound(location=request.route_url('forgotpass'))
    # if submitted:
    if 'form.submitted' in request.params:
        password = request.params.get('password')
        password2 = request.params.get('password2')
        if modifyUser(request, item, "", "", password, password2, passwordonly=True) is False:
            return dict(url=request.route_url("resetpass", jwe=jwe))
        # if success:
        request.session.flash("s|Password reset successfully.")
        return HTTPFound(location=request.route_url('login'))
    return dict(url=request.route_url("resetpass", jwe=jwe))

@view_config(route_name='forgotpass', renderer='../templates/forgotpass.jinja2')
def forgotpass(request):
    if request.user:
        # already logged in, redirect to home
        return HTTPFound(location=request.route_url('home'))
    next_url = request.params.get('next', None)
    if not next_url:
        next_url = request.route_url('home')
    login = ''
    if 'form.submitted' in request.params:
        login = request.params.get('email')
        item = request.dbsession.query(User).filter_by(email=login).first()
        if item is not None:
            # Generate link:
            key = JWK(**loads(request.registry.settings["jwt.secret"]))
            mins = request.registry.settings["jwt.expire"]
            payload = dumps({"id": item.id, "dt": timegm(gmtime()),
                "hash": hexlify(item.password_hash).decode("utf-8")})
            token = JWE(payload.encode('utf-8'), json_encode({"alg": "A256KW", "enc": "A256CBC-HS512"}))
            token.add_recipient(key)
            link = request.route_url("resetpass", jwe=token.serialize(True))
            message = Message(subject="VS Leaderboard - Reset Password",
                  recipients=[item.email],
                  body="To reset your password, please click: \n{0}\n".format(link) +
                    "This link will expire in {0} minutes.".format(mins))
            request.mailer.send(message)
        request.session.flash("s|If that e-mail address is used it will receive a password reset link.")

    return dict(url=request.route_url('forgotpass'), next_url=next_url, login=login,)

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    next_url = request.route_url('home')
    return HTTPFound(location=next_url, headers=headers)

@forbidden_view_config()
def forbidden_view(request):
    next_url = request.route_url('login', _query={'next': request.url})
    return HTTPFound(location=next_url)
