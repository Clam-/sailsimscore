from ipaddress import ip_address
from datetime import datetime
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    Boolean,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship

from .meta import Base
from .recordingdata import Course, Gusts
from .ip import IPMixin
from .windspeed import WindSpeedMixin
from .eventassoc import association_table, allowed_table

class Event(IPMixin, WindSpeedMixin, Base):
    """ The SQLAlchemy declarative model class for an Event object. """
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    order = Column(Integer)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    current = Column(Boolean(name="current"))
    notes = Column(Text)
    # Restrictions
    gusts = Column(Enum(Gusts), nullable=False, name="gusts")
    rams = Column(Boolean(name="rams"))
    course = Column(Enum(Course), nullable=False, name="course")
    bigcourse = Column(Boolean(name="bigcourse"))
    laps = Column(Integer) # 0 means any
    allowprevious = Column(Boolean(name="allowprevious"))
    windspeed = Column(Numeric)

    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref='events')

    recordings = relationship("Recording", secondary=association_table,
        back_populates="events")
    allowed_boats = relationship("Boat", secondary=allowed_table,
        back_populates="events")

    comments = relationship("CommentEventAssoc")

    @property
    def desc(self): return self.name

    # default new event values
    def __init__(self):
        self.course = Course.Triangular
        self.gusts = Gusts.none
        self.rams = False
        self.bigcourse = False
        self.laps = 1
        self.windspeedknt = 12
        self.allowprevious = True

    def active(self):
        return self.start <= datetime.utcnow() <= self.end
