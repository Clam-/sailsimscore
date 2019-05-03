from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean
)

from .meta import Base

class Event(Base):
    """ The SQLAlchemy declarative model class for an Event object. """
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    active = Column(Boolean)
