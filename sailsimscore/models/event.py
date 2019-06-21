from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    Text,
    Boolean
)
from sqlalchemy.orm import relationship

from .meta import Base

association_table = Table('eventrecordings', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id')),
    Column('recording_id', Integer, ForeignKey('recordings.id'))
)

class Event(Base):
    """ The SQLAlchemy declarative model class for an Event object. """
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    order = Column(Integer)
    active = Column(Boolean(name="active"))
    current = Column(Boolean(name="current"))
    notes = Column(Text)

    user_id = Column(ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref='events')

    recordings = relationship("Recording", secondary=association_table,
        back_populates="events")
