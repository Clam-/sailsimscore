from ipaddress import ip_address
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    Boolean,
    DateTime,
    Enum,
)
from sqlalchemy.orm import relationship

from .meta import Base
from .recordingdata import Course, Gusts
from .ip import IPMixin
from .eventassoc import association_table

class Event(IPMixin, Base):
    """ The SQLAlchemy declarative model class for an Event object. """
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    order = Column(Integer)
    start = Column(DateTime)
    end = Column(DateTime)
    current = Column(Boolean(name="current"))
    notes = Column(Text)
    # Restrictions
    gusts = Column(Enum(Gusts), nullable=False, name="gusts")
    rams = Column(Boolean(name="rams"))
    course = Column(Enum(Course), nullable=False, name="course")
    bigcourse = Column(Boolean(name="bigcourse"))
    laps = Column(Integer) # 0 means any

    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref='events')

    recordings = relationship("Recording", secondary=association_table,
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
