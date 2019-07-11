from ipaddress import ip_address
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship

from .meta import Base
from .ip import IPMixin

association_table = Table('eventrecordings', Base.metadata,
    Column('event_id', Integer, ForeignKey('event.id')),
    Column('recording_id', Integer, ForeignKey('recording.id'))
)

class Event(IPMixin, Base):
    """ The SQLAlchemy declarative model class for an Event object. """
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    order = Column(Integer)
    active = Column(Boolean(name="active"))
    current = Column(Boolean(name="current"))
    notes = Column(Text)

    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref='events')

    recordings = relationship("Recording", secondary=association_table,
        back_populates="events")

    comments = relationship("CommentEventAssoc")

    @property
    def desc(self): return self.name
