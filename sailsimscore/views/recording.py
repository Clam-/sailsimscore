from pyramid.compat import escape
import re
import markdown
from datetime import datetime
from csv import reader
from io import TextIOWrapper
from tempfile import TemporaryFile
from shutil import copyfileobj, move, copyfile
from os.path import join, relpath
from os import makedirs, error
from hashlib import sha224
from binascii import hexlify

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..models import Recording, Event, Boat
from ..models.recording import Course, Gusts, KNOTS_TO_M

@view_config(route_name='list_recording', renderer='../templates/list_recording.jinja2')
def list_recording(request):
    items = request.dbsession.query(Recording)
    return dict(items=items)

@view_config(route_name='view_recording', renderer='../templates/view_recording.jinja2',
             permission='view')
def view_recording(request):
    item = request.context.item
    edit_url = request.route_url('edit_recording', iid=item.id)
    return dict(item=item, edit_url=edit_url)

@view_config(route_name='edit_recording', renderer='../templates/edit_recording.jinja2',
             permission='edit')
def edit_recording(request):
    item = request.context.item
    if 'form.submitted' in request.params:
        item.notes = request.params.get('notes')
        #Events submitted
        next_url = request.route_url('view_event', iid=item.id)
        return HTTPFound(location=next_url)
    return dict(
        item=item,
        save_url=request.route_url('edit_recording', iid=item.id),
        )

@view_config(route_name='add_recording_to_event', permission='create')
def add_recording_to_event(request):
    eid = request.matchdict['eid']
    recording = request.context.item
    event = request.dbsession.query(Event).filter_by(id=eid).first()
    if not event:
        request.session.flash("d|Event not found.")
        raise HTTPNotFound
    if not recording:
        request.session.flash("d|Recording not found.")
        raise HTTPNotFound
    prev = request.route_url("view_event", iid=event.id)
    return add_recording_wcheck(request, event, recording, prev)

def add_recording_wcheck(request, event, recording, prev):
    if not event.allowprevious:
        request.session.flash("d|Previous recordings not allowed.")
        raise HTTPFound(location=prev)
    if recording.datetime < event.start:
        request.session.flash("d|Recording submitted before event start.")
        raise HTTPFound(location=prev)
    if recording.datetime > event.end:
        request.session.flash("d|Recording submitted after event end.")
        raise HTTPFound(location=prev)
    if recording.windspeed > event.windspeed:
        request.session.flash("d|Recording windspeed too high.")
        raise HTTPFound(location=prev)
    if recording.bigcourse != event.bigcourse:
        request.session.flash("d|Wrong course size set.")
        raise HTTPFound(location=prev)
    if recording in event.recordings:
        request.session.flash("d|Recording already submitted.")
        raise HTTPFound(location=prev)
    if event.gusts != Gusts.any and recording.gusts !=event.gusts:
        request.session.flash("d|Recording gust setting incorrect.")
        raise HTTPFound(location=prev)
    if event.rams and recording.rams != event.rams:
        request.session.flash("d|Recording ram setting incorrect.")
        raise HTTPFound(location=prev)
    if event.allowed_boats and recording.boat not in event.allowed_boats:
        request.session.flash("d|Recording boat not allowed.")
        raise HTTPFound(location=prev)
    if event.laps > 0 and recording.laps != event.laps:
        request.session.flash("d|Recording laps setting incorrect.")
        raise HTTPFound(location=prev)
    event.recordings.append(recording)
    return HTTPFound(location=prev)

@view_config(route_name='add_recording_id', renderer='../templates/add_recording.jinja2',
             permission='create')
@view_config(route_name='add_recording', renderer='../templates/add_recording.jinja2',
             permission='create')
def add_recording(request):
    item = request.context.item
    prev = request.route_url("list_recording")
    event = False
    if request.matchdict['eventid']:
        event = request.dbsession.query(Event).filter_by(id=request.matchdict['eventid']).first()
        if event is None:
            request.session.flash("d|Event not found.")
            raise HTTPNotFound
        prev = request.route_url("view_event", iid=event.id)
    recordings = None
    if 'form.submitted' not in request.params:
        # fetch available recordings for selection
        if event and event.allowprevious:
            recordings = request.dbsession.query(Recording).filter(Recording.user==request.user).\
                filter(Recording.datetime<=event.end).filter(Recording.datetime>=event.start).\
                filter(Recording.windspeed<=event.windspeed).\
                filter(Recording.bigcourse==event.bigcourse).\
                filter(~Recording.events.any(Event.id == event.id))
            if event.gusts != Gusts.any: recordings = recordings.filter(Recording.gusts==event.gusts)
            if event.rams: recordings = recordings.filter(Recording.rams==event.rams)
            if event.allowed_boats: recordings = recordings.filter(Recording.boat in event.allowed_boats)
            if event.laps > 0: recordings = recordings.filter(Recording.laps==event.laps)

    if 'form.submitted' in request.params:
        item.user = request.user
        item.ip = request.remote_addr
        if event and (datetime.utcnow() > event.end):
            request.session.flash("d|Sorry, event is no longer taking recordings.")
            raise HTTPFound(location=prev)
        f = TemporaryFile()
        # move file
        if "fileupload" in request.POST and hasattr(request.POST['fileupload'], 'filename'):
            copyfileobj(request.POST["fileupload"].file, f)
        else:
            #error
            request.session.flash("d|Missing file.")
            raise HTTPFound(location=prev)
        ## Read file
        f.seek(0)
        metadata = process_recording(f, request.dbsession)
        if metadata["error"]:
            #request.dbsession.rollback()
            request.session.flash("d|%s" % metadata["reason"])
            raise HTTPFound(location=prev)
        f = metadata["f"] # get file obj after TextIOWrapper hijacks it.
        item.time = metadata["finishtime"]
        item.datetime = datetime.utcnow()
        item.hash = shadigest(f)
        # check if recording exists already
        with request.dbsession.no_autoflush:
            if request.dbsession.query(Recording).filter(Recording.hash == item.hash).first():
                request.session.flash("d|%s" % "Recording already uploaded. Cannot re-upload.")
                raise HTTPFound(location=prev)
        # Add metadata minus note.
        item.bigcourse = metadata["bigcourse"]
        item.modified = metadata["modified"]
        item.course = metadata["coursetype"]
        item.laps = metadata["laps"]
        item.gusts = metadata["gusts"]
        if item.gusts == Gusts.none and metadata["gustspeed"] > 0:
            # spit warning out
            request.session.flash("d|%s" % "Gust type changed after recording started. Can't accept this recording. Set Gusts appropriately before starting the course.")
            raise HTTPFound(location=prev)
        item.windspeed = metadata["windspeed"]
        item.rams = metadata["rams"]
        item.boat = metadata["boattype"]
        # copy/move recording to final location and store
        f.seek(0)
        min, sec = divmod(item.time, 60)
        h = hexlify(item.hash).decode("utf-8")
        folder = join(request.registry.settings["recordingstorage"], h[:2])
        try: makedirs(folder)
        except error: pass
        loc = join(folder,
            "{0}.{1:.3f}-{2}-{3}.sbp".format(min, sec, item.course.name, h[:4]))
        with open(loc, "wb") as outfile:
            copyfileobj(f, outfile)
        item.fileloc = relpath(loc, request.registry.settings["recordingstorage"])

        request.dbsession.add(item)
        request.dbsession.flush()
        if event:
            return add_recording_wcheck(request, event, item, prev)
        return HTTPFound(location=prev)
    save_url = request.route_url('add_recording') if not event else request.route_url('add_recording_id', eventid=event.id)
    return dict(item=item, save_url=save_url, event=event, recordings=recordings)

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
    metadata["f"] = ft.detach()
    return metadata

def metadataError(s):
    return {"error" : True, "reason" : s}

def version_1_header(header, metadata, dbsession):
    if len(header) != 10:
        return metadataError("Unsupported recording version")
    else:
        metadata["modified"] = header[1] == "1"
        boatid = header[2]
        boatex = header[9]
        if boatid == "1000" and boatex == "0":
            return metadataError("Unsupported boat/laser type.")
        elif boatid == "1000":
            boatid = boatex
        with dbsession.no_autoflush:
            boat = dbsession.query(Boat).filter(Boat.id == int(boatid)).first()
            if not boat:
                return metadataError("Unsupported Boat Type (%s,%s)" % (boatid, boatex))
            metadata["boattype"] = boat
        metadata["finishtime"] = 99999 if header[3] == "0" else float(header[3])
        metadata["coursetype"] = Course(int(header[4]))
        metadata["bigcourse"] = header[5] == "1"
        metadata["laps"] = int(header[6])
        # need to read recording file to determine if Gusts were on.
        metadata["gusts"] = Gusts(int(header[7]))
        metadata["rams"] = header[8] == "1"
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
