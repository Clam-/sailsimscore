from pyramid.compat import escape
import re
import markdown
from datetime import datetime
from csv import reader
from io import TextIOWrapper
from tempfile import TemporaryFile
from shutil import copyfileobj
from hashlib import sha224

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..models import Recording, Event, Boat

@view_config(route_name='list_recording', renderer='../templates/list_recording.jinja2')
def list_recording(request):
    items = request.dbsession.query(Recording)
    return dict(items=items)

@view_config(route_name='view_recording', renderer='../templates/view_recording.jinja2',
             permission='view')
def view_recording(request):
    item = request.context.item
    edit_url = request.route_url('edit_recording', iid=item.id)
    return dict(item=item, edit_url=edit_url,
        notes=markdown.markdown(item.notes if item.notes else "", output_format="html5"))

@view_config(route_name='edit_recording', renderer='../templates/edit_recording.jinja2',
             permission='edit')
def edit_recording(request):
    item = request.context.item
    if 'form.submitted' in request.params:
        item.notes = request.params['notes']
        #Events submitted
        next_url = request.route_url('view_event', iid=item.id)
        return HTTPFound(location=next_url)
    return dict(
        item=item,
        save_url=request.route_url('edit_event', iid=item.id),
        )

@view_config(route_name='add_recording_id', renderer='../templates/add_recording.jinja2',
             permission='create')
@view_config(route_name='add_recording', renderer='../templates/add_recording.jinja2',
             permission='create')
def add_recording(request):
    item = request.context.item
    prev = request.route_url("list_recording")
    if request.matchdict['eventid']:
        event = request.dbsession.query(Event).filter_by(id=request.matchdict['eventid']).first()
        if item is None: raise HTTPNotFound
        item.event = event
        prev = request.route_url("view_event", iid=event.id)
    if 'form.submitted' in request.params:
        item.user = request.user
        if item.event and not item.event.active:
            request.session.flash("d|Sorry, event is no longer taking recordings.")
            return HTTPFound(location=prev)
        f = TemporaryFile()
        # move file
        if "fileupload" in request.POST and request.POST["fileupload"].file:
            copyfileobj(request.POST["fileupload"].file, f)
        else:
            #error
            request.session.flash("d|Missing file.")
            return HTTPFound(location=prev)
        ## Read file
        f.seek(0)
        metadata = process_recording(f, request.dbsession)
        if metadata["error"]:
            #request.dbsession.rollback()
            request.session.flash("d|%s" % metadata["reason"])
            raise HTTPFound(location=prev)
        aaa
        item.time = metadata["finishtime"]
        item.datetime = datetime.now()
        item.hash = shadigest(f)
        item.bigcourse = metadata["bigcourse"]
        item.modified = metadata["modified"]
        item.course = metadata["coursetype"]
        g = Gusts.none
        if metadata["gustspeed"] > 0:
            g = metadata["repeatablegusts"]
        item.gusts = g
        item.boat = metadata["boattype"]
        # Add metadata minus note.
        request.dbsession.add(item)
        request.dbsession.flush()
        if item.event: item.event.recordings.append(item)
        return edit_event(request)
    save_url = request.route_url('add_recording') if not item.event else request.route_url('add_recording_id', eventid=item.event.id)
    return dict(item=item, save_url=save_url)


def process_recording(f, dbsession):
    f.seek(0)
    ft = TextIOWrapper(f, encoding='ascii', errors='replace')
    csvreader = reader(ft, delimiter='\t')
    header = next(csvreader)
    metadata = {"error" : False}
    version = "0"
    # check header
    if header[0].startswith("@"):
        #version
        version = header[0].lstrip("@")
        headerfunc = "version_%s_header" % version
        if headerfunc in globals():
            metadata = globals()[headerfunc](header, metadata, dbsession)
        else:
            return metadataError("Unsupported recording version")
    else:
        return metadataError("Unsupported recording version")
    #process rest:
    rowsfunc = "version_%s_rows" % version
    if rowsfunc in globals():
        metadata = globals()[rowsfunc](csvreader, metadata, dbsession)
    else:
        return metadataError("Rows parser missing.")
    return metadata

def metadataError(s):
    return {"error" : True, "reason" : s}

def version_1_header(header, metadata, dbsession):
    if len(header) != 8:
        return metadataError("Unsupported recording version")
    else:
        metadata["changed"] = True if header[1] == "1" else False
        with dbsession.no_autoflush:
            boat = dbsession.query(Boat, ).filter(Boat.id == int(header[2])).first()
            if not boat:
                return metadataError("Unsupported Boat Type (%s)" % header[2])
            metadata["boattype"] = boat
        metadata["finishtime"] = 9999999 if header[3] == "0" else float(header[3])
        metadata["coursetype"] = Course(int(header[4]))
        metadata["bigcourse"] = True if header[5] == "1" else False
        metadata["laps"] = int(header[6])
        # need to read recording file to determine if Gusts were on.
        metadata["repeatablegusts"] = Gusts.repeat if header[6] == "1" else Gusts.random
    return metadata

def version_1_rows(csvreader, metadata, dbsession):
    windspeed = 0
    gustspeed = 0
    for row in csvreader:
        # windstrength = 15 guststrength = 17
        tw = float(row[15])
        windspeed = tw if tw > windspeed else windspeed
        tg = float(row[17])
        gustspeed = tg if tg > gustspeed else gustspeed
    metadata["windspeed"] = windspeed
    metadata["gustspeed"] = gustspeed if gustspeed > windspeed else 0
    return metadata

def shadigest(f):
    hash = sha224()
    f.seek(0)
    for chunk in iter(lambda: f.read(4096), b""):
        hash.update(chunk)
    return hash.digest()
