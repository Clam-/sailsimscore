from ipaddress import ip_address
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
)

from .meta import Base

association_table = Table('eventrecordings', Base.metadata,
    Column('event_id', Integer, ForeignKey('event.id')),
    Column('recording_id', Integer, ForeignKey('recording.id'))
)

allowed_table = Table('allowedboats', Base.metadata,
    Column('event_id', Integer, ForeignKey('event.id')),
    Column('boat_id', Integer, ForeignKey('boat.id'))
)
