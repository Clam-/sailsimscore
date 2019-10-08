from pyramid.compat import escape
from dateutil import parser
from datetime import datetime

import re
import markdown

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..models import Event
from ..models.recordingdata import Course, Gusts, KNOTS_TO_M
from ..models.eventassoc import association_table

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
    return dict(item=item, edit_url=edit_url)

@view_config(route_name='edit_event', renderer='../templates/edit_event.jinja2',
             permission='edit')
def edit_event(request):
    item = request.context.item

    if 'form.submitted' in request.params:
        # check if have dates
        if 'eventStart-dt' in request.params and request.params['eventStart-dt']:
            item.start = parser.isoparse(request.params['eventStart-dt'])
            if 'eventEnd-dt' in request.params and request.params['eventEnd-dt']:
                item.end = parser.isoparse(request.params['eventEnd-dt'])
            else:
                #bail
                request.session.flash("d|Event requires an End datetime")
                raise HTTPFound(location=request.prev)
        else:
            #bail
            request.session.flash("d|Event requires a Start datetime")
            raise HTTPFound(location=request.prev)
        prevCurrent = item.current
        newCurrent = 'currentCheck' in request.params
        if newCurrent and not prevCurrent:
            request.dbsession.query(Event).update({Event.current:False})
        item.name = request.params['eventName']
        item.order = request.params['orderIndex']
        #Restrictions
        item.gusts = Gusts(int(request.params['gustsRadio']))
        item.rams = 'ramsCheck' in request.params
        item.course = Course(int(request.params['courseRadio']))
        item.bigcourse = True if request.params['bigRadio'] == "yes" else False
        item.laps = int(request.params['laps'])
        item.windspeed = int(float(request.params['windspeed'])) * KNOTS_TO_M
        item.allowprevious = 'previousCheck' not in request.params

        item.current = newCurrent
        item.notes = request.params['notes']
        item.modip = request.remote_addr
        next_url = request.route_url('view_event', iid=item.id)
        return HTTPFound(location=next_url)
    # get boat list for restriction selection
    boats = request.dbsession.query(Boat).all()
    return dict(
        item=item,
        save_url=request.route_url('edit_event', iid=item.id),
        )

@view_config(route_name='add_event', renderer='../templates/edit_event.jinja2',
             permission='create')
def add_event(request):
    item = request.context.item
    if item.id:
        request.prev = request.route_url("edit_event", iid=item.id)
    else:
        request.prev = request.route_url("list_event")
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

@view_config(route_name='event_rm_recording', renderer='../templates/remove_recording.jinja2',
             permission='edit')
def event_rm_recording(request):
    eid = request.matchdict['eid']
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
