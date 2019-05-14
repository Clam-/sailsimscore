from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    Numeric,
    DateTime,
    BINARY,
)
from sqlalchemy.orm import relationship

from .meta import Base

#object/model/table for all recordings. Master list
class Recording(Base):
    """ The SQLAlchemy declarative model class for a Recording object. """
    __tablename__ = 'recordings'
    id = Column(Integer, primary_key=True)
    time = Column(Numeric)
    note = Column(Text)
    datetime = Column(DateTime)
    hash = Column(BINARY(20)) #hashlib.sha224(b"content").digest()

    user_id = Column(ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref='recordings')

    boat_id = Column(ForeignKey('boats.id'), nullable=False)
    boat = relationship('Boat', backref='recordings')

    comments = relationship("CommentAssociation")
