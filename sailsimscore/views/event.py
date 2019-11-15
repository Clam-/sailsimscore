from pyramid.compat import escape
from dateutil import parser
from datetime import datetime

import re
import markdown

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..models import Event, Boat
from ..models.recordingdata import Course, Gusts, KNOTS_TO_M
from ..models.eventassoc import association_table
from ..views.utils import filter_recordings
from ..models.paginate import paginator

@view_config(route_name='list_event', renderer='../templates/list_event.jinja2')
def list_event(request):
    items = request.dbsession.query(Event)
    now = datetime.utcnow()
    return dict(items=items, now=now)

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
    boats = ", ".join((b.desc for b in item.allowed_boats)) if item.allowed_boats else "Any"
    # filter
    q = filter_recordings(request.dbsession,
        request.params.get("user", None),
        request.params.get("boat", None),
        item.recordings
    )
    #pager
    recordings = paginator(request, q)
    return dict(item=item, edit_url=edit_url, boats=boats, recordings=recordings)

def validate_date_event(request, item):
    # check if have dates
    if request.params.get('eventStart-dt'):
        item.start = parser.isoparse(request.params.get('eventStart-dt'))
        if request.params.get('eventEnd-dt'):
            item.end = parser.isoparse(request.params.get('eventEnd-dt'))
        else:
            #bail
            request.session.flash("d|Event requires an End datetime")
            return False
    else:
        #bail
        request.session.flash("d|Event requires a Start datetime")
        return False
    return True

def build_boat_respdict(request, item, url):
    # get boat list for restriction selection
    # ["Any", None], [Gusts.random.name, Gusts.random.value],
    boats = [[b.name, b.id] for b in request.dbsession.query(Boat).all()]
    boats.insert(0, ["Any", ""])
    allowed = [ b.id for b in item.allowed_boats]
    if allowed == []: allowed = [""]
    return dict(
        item=item,
        save_url=url,
        boats=boats, allowed=allowed,
        )

def build_boat_list(boats, dbsession):
    if not boats or '' in boats:
        return []
    boatobjs = dbsession.query(Boat).filter(Boat.id.in_(boats)).all()
    return boatobjs

@view_config(route_name='edit_event', renderer='../templates/edit_event.jinja2',
             permission='edit')
def edit_event(request):
    item = request.context.item

    if 'form.submitted' in request.params:
        if not validate_date_event(request, item):
            request.dbsession.rollback()
            return dict(item=item, save_url=request.route_url('edit_event', iid=item.id))

        prevCurrent = item.current
        newCurrent = 'currentCheck' in request.params
        if newCurrent and not prevCurrent:
            request.dbsession.query(Event).update({Event.current:False})
        item.name = request.params.get('eventName')
        item.order = request.params.get('orderIndex')
        #Restrictions
        item.gusts = Gusts(int(request.params.get('gustsRadio', Gusts.none)))
        item.rams = 'ramsCheck' in request.params
        item.course = Course(int(request.params.get('courseRadio', Course.Triangular)))
        item.bigcourse = True if request.params.get('bigRadio') == "yes" else False
        item.laps = int(request.params.get('laps', 1))
        item.windspeed = int(float(request.params.get('windspeed'))) * KNOTS_TO_M
        item.allowprevious = 'previousCheck' not in request.params
        item.allowed_boats = build_boat_list(request.params.getall('boatsAllow'), request.dbsession)
        item.current = newCurrent
        item.notes = request.params.get('notes')
        item.modip = request.remote_addr
        next_url = request.route_url('view_event', iid=item.id)
        return HTTPFound(location=next_url)
    return build_boat_respdict(request, item, request.route_url('edit_event', iid=item.id))

@view_config(route_name='add_event', renderer='../templates/edit_event.jinja2',
             permission='create')
def add_event(request):
    item = request.context.item
    save_url = request.route_url('add_event')
    if 'form.submitted' in request.params:
        item.user = request.user
        item.name = request.params.get('eventName')
        if not item.name:
            request.session.flash("d|Event requires a Name")
            request.dbsession.rollback()
            return build_boat_respdict(request, item, save_url)
        if not validate_date_event(request, item):
            request.dbsession.rollback()
            return build_boat_respdict(request, item, save_url)
        item.createdip = request.remote_addr
        request.dbsession.add(item)
        request.dbsession.flush()
        return edit_event(request)
    return build_boat_respdict(request, item, save_url)

@view_config(route_name='delete_event', renderer='../templates/delete_item.jinja2',
             permission='edit')
def del_event(request):
    item = request.context.item
    del_url = request.route_url('delete_event', iid=item.id)
    if 'form.submitted' in request.params:
        request.dbsession.delete(item)
        return HTTPFound(location=request.route_url('list_event'))
    return dict(item=item, del_url=del_url)

@view_config(route_name='event_rm_recording', renderer='../templates/remove_recording.jinja2',
             permission='edit')
def event_rm_recording(request):
    eid = request.matchdict.get('eid')
    item = request.context.item
    rid = item.id
    event = request.dbsession.query(Event).filter(Event.id==eid).first()
    if not event:
        raise HTTPNotFound("Event not found.")
    # delete straight from association table
    assoc = request.dbsession.query(association_table).filter(
        (association_table.c.event_id == eid) and (association_table.c.recording_id == rid)).first()
    #aaa
    if not assoc:
            request.session.flash("d|Recording not found for event.")
            return HTTPFound(location=request.route_url('view_event', iid=eid))

    del_url = request.route_url('event_rm_recording', iid=item.id, eid=eid)
    if 'form.submitted' in request.params:
        #Remove item from event
        event.recordings.remove(item)
        return HTTPFound(location=request.route_url('view_event', iid=eid))
    return dict(item=item, del_url=del_url, event=event)
