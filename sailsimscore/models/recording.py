from enum import Enum as pyEnum
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
class Recording(Base):
    """ The SQLAlchemy declarative model class for a Recording object. """
    __tablename__ = 'recordings'
    id = Column(Integer, primary_key=True)
    time = Column(Numeric)
    note = Column(Text)
    datetime = Column(DateTime)
    hash = Column(BINARY(20)) #hashlib.sha224(b"content").digest()
    bigcourse = Column(Boolean(name="bigcourse"))
    modified = Column(Boolean(name="modified"))
    course = Column(Enum(Course), nullable=False, name="course")
    gusts = Column(Enum(Gusts), nullable=False, name="gusts")

    user_id = Column(ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref='recordings')

    boat_id = Column(ForeignKey('boats.id'), nullable=False)
    boat = relationship('Boat', backref='recordings')

    comments = relationship("CommentAssociation")

    events = relationship("Event", secondary=association_table,
        back_populates="recordings")
