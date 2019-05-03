from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean
)

from .meta import Base

class EventAssociation(Base):
    __tablename__ = 'eventrecordings'
    event_id = Column(Integer, ForeignKey('events.id'), primary_key=True)
    recording_id = Column(Integer, ForeignKey('recordings.id'), primary_key=True)

    recording = relationship("Recording")
