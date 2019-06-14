from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    Boolean
)
from sqlalchemy.orm import relationship

from .meta import Base

class Event(Base):
    """ The SQLAlchemy declarative model class for an Event object. """
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    order = Column(Integer)
    active = Column(Boolean(name="active"))

class EventAssociation(Base):
    __tablename__ = 'eventrecordings'
    event_id = Column(Integer, ForeignKey('events.id'), primary_key=True)
    recording_id = Column(Integer, ForeignKey('recordings.id'), primary_key=True)

    recording = relationship("Recording")
