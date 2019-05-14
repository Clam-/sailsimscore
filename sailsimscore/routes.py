from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPFound,
)
from pyramid.security import (
    Allow,
    Everyone,
    Authenticated
)

from . import models

def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    config.add_route('list_event', '/event')
    config.add_route('view_event', '/event/{iid}', factory=event_factory)
    config.add_route('add_event', '/event/new', factory=new_event_factory)
    config.add_route('edit_event', '/event/{iid}/edit', factory=event_factory)

    config.add_route('list_recording', '/recording')
    config.add_route('view_recording', '/recording/{iid}', factory=recording_factory)
    config.add_route('add_recording', '/recording/new/{eventid}', factory=new_recording_factory) # POST only
    config.add_route('edit_recording', '/recording/{iid}/edit', factory=recording_factory)

    config.add_route('list_boat', '/boat')
    config.add_route('view_boat', '/boat/{iid}', factory=boat_factory)
    config.add_route('add_boat', '/boat/new', factory=new_boat_factory)
    config.add_route('edit_boat', '/boat/{iid}/edit', factory=boat_factory)

    config.add_route('list_comment', '/comment')
    config.add_route('add_comment', '/comment/new/{recordingid}', factory=new_comment_factory)
    config.add_route('add_comment_post', '/comment/new', factory=new_comment_factory, request_method="POST") # POST only
    config.add_route('edit_comment', '/comment/{iid}/edit', factory=comment_factory)


def gen_factory(CLS, request):
    iid =  request.matchdict['iid']
    item = request.dbsession.query(CLS).filter_by(id=iid).first()
    if item is None: raise HTTPNotFound
    return AdminItem(item)

def boat_factory(request):
    return gen_factory(models.Boat, request)
def new_boat_factory(request):
    return new_admin_factory(request, models.Boat)

def event_factory(request):
    return gen_factory(models.Event, request)
def new_event_factory(request):
    return new_admin_factory(request, models.Event)

def new_admin_factory(request, CLS):
    return AdminItem(CLS())
class AdminItem(object):
    def __init__(self, item):
        self.item = item

    def __acl__(self):
        return [
            (Allow, 'role:admin', 'create'),
            (Allow, 'role:admin', 'edit'),
        ]

class UserItem(object):
    def __init__(self, item):
        self.item = item

    def __acl__(self):
        return [
            (Allow, Everyone, 'view'),
            (Allow, Authenticated, 'create'),
            (Allow, 'role:admin', 'edit'),
            (Allow, str(self.item.user_id), 'edit'),
        ]

#factory for user generated ACLs/query
def gen_user_factory(CLS, request):
    iid =  request.matchdict['iid']
    item = request.dbsession.query(CLS).filter_by(id=iid).first()
    if item is None: raise HTTPNotFound
    return UserItem(item)

def recording_factory(request):
    return gen_user_factory(models.Recording, request)

def comment_factory(request):
    return gen_user_factory(models.Comment, request)
