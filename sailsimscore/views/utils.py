from ..models import Recording, User, Boat

def filter_recordings(dbsession, user, boat, q):
    filters = []
    # query build
    if user:
        q = q.filter(Recording.user_id==user)
        userobj = dbsession.query(User).filter(User.id == user).first()
        if userobj: filters.append("User: {0}".format(userobj.name))
        else: filters.append("User: {0}".format("Unknown User"))
    if boat:
        q = q.filter(Recording.boat_id==boat)
        boatobj = dbsession.query(Boat).filter(Boat.id == boat).first()
        if boatobj: filters.append("Boat: {0}".format(boatobj.name))
        else: filters.append("Boat: {0}".format("Unknown Boat"))
    q = q.order_by(Recording.time, Recording.id)
    return q
