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
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('current_event', '/current')
    config.add_route('list_event', '/event')
    config.add_route('add_event', '/event/new', factory=new_event_factory)
    config.add_route('view_event', '/event/{iid}', factory=event_factory)
    config.add_route('edit_event', '/event/{iid}/edit', factory=event_factory)
    config.add_route('delete_event_prompt', '/event/{iid}/delete', factory=event_factory)
    config.add_route('delete_event', '/event/{iid}/delete', factory=event_factory, request_method="POST")

    config.add_route('list_recording', '/recording')
    config.add_route('view_recording', '/recording/{iid}', factory=recording_factory)
    config.add_route('add_recording', '/recording/new/{eventid}', factory=new_recording_factory) # POST only
    config.add_route('edit_recording', '/recording/{iid}/edit', factory=recording_factory)
    config.add_route('delete_recording_prompt', '/recording/{iid}/delete', factory=recording_factory)
    config.add_route('delete_recording', '/recording/{iid}/delete', factory=recording_factory, request_method="POST")

    config.add_route('list_boat', '/boat')
    config.add_route('view_boat', '/boat/{iid}', factory=boat_factory)
    config.add_route('add_boat', '/boat/new', factory=new_boat_factory)
    config.add_route('edit_boat', '/boat/{iid}/edit', factory=boat_factory)
    config.add_route('delete_boat_prompt', '/boat/{iid}/delete', factory=boat_factory)
    config.add_route('delete_boat', '/boat/{iid}/delete', factory=boat_factory, request_method="POST")

    config.add_route('list_comment', '/comment')
    config.add_route('add_comment', '/comment/new/{recordingid}', factory=new_comment_factory)
    config.add_route('add_comment_post', '/comment/new', factory=new_comment_factory, request_method="POST") # POST only
    config.add_route('edit_comment', '/comment/{iid}/edit', factory=comment_factory)
    config.add_route('delete_comment_prompt', '/comment/{iid}/delete', factory=comment_factory)
    config.add_route('delete_comment', '/comment/{iid}/delete', factory=comment_factory, request_method="POST")


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
            (Allow, Everyone, 'view'),
            (Allow, 'role:A', 'create'),
            (Allow, 'role:A', 'edit'),
        ]
def new_user_factory(request, CLS):
    return UserItem(CLS())

class UserItem(object):
    def __init__(self, item):
        self.item = item

    def __acl__(self):
        base = [
            (Allow, Everyone, 'view'),
            (Allow, Authenticated, 'create'),
            (Allow, 'role:A', 'edit')
        ]
        if hasattr(self.item, "user_id"):
            base.append((Allow, str(self.item.user_id), 'edit'),)
        else: print("MISSING USER_ID? on %s" % self.item)
        return base

#factory for user generated content
def gen_user_factory(CLS, request):
    iid =  request.matchdict['iid']
    item = request.dbsession.query(CLS).filter_by(id=iid).first()
    if item is None: raise HTTPNotFound
    return UserItem(item)

def recording_factory(request):
    return gen_user_factory(models.Recording, request)
def new_recording_factory(request):
    return new_user_factory(models.Recording, request)

def comment_factory(request):
    return gen_user_factory(models.Comment, request)
def new_comment_factory(request):
    return new_user_factory(models.Comment, request)
