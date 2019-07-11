from enum import Enum as pyEnum
from ipaddress import ip_address
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    Numeric,
    DateTime,
    Boolean,
    Enum,
    BINARY,
)
from sqlalchemy.orm import relationship

from .meta import Base
from .ip import IPMixin
from .event import association_table

class Course(pyEnum):
    none = 0
    CrossWind = 1
    Trapezoidal = 2
    Triangular = 3
    UpDownWind = 4

class Gusts(pyEnum):
    none = "N"
    random = "A"
    repeat = "E"

#object/model/table for all recordings. Master list
class Recording(IPMixin, Base):
    """ The SQLAlchemy declarative model class for a Recording object. """
    id = Column(Integer, primary_key=True)
    time = Column(Numeric)
    notes = Column(Text)
    _datetime = Column(DateTime)
    hash = Column(BINARY(20)) #hashlib.sha224(b"content").digest()
    bigcourse = Column(Boolean(name="bigcourse"))
    laps = Column(Integer)
    modified = Column(Boolean(name="modified"))
    course = Column(Enum(Course), nullable=False, name="course")
    gusts = Column(Enum(Gusts), nullable=False, name="gusts")
    fileloc = Column(Text)
    deleted = Column(Boolean(name="deleted"))

    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref='recordings')

    boat_id = Column(ForeignKey('boat.id'), nullable=False)
    boat = relationship('Boat', backref='recordings')

    comments = relationship("CommentRecAssoc")

    events = relationship("Event", secondary=association_table,
        back_populates="recordings")

    @property
    def desc(self):
        return "{0}, {1}, {2}".format(self.course, self.datetime, self.notes)
    @property
    def datetime(self):
        return self._datetime.isoformat(timespec='minutes')
    @datetime.setter
    def datetime(self, value):
        self._datetime = value
