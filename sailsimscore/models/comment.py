from ipaddress import ip_address
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    Boolean,
    BINARY,
)
from sqlalchemy.orm import relationship

from .meta import Base
from .ip import IPMixin

class Comment(Base):
    """ The SQLAlchemy declarative model class for a Comment object. """
    id = Column(Integer, primary_key=True)
    content = Column(Text)

    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', backref='comments')
    deleted = Column(Boolean(name="deleted"))

    @property
    def desc(self): return self.content

class CommentRecAssoc(Base):
    recording_id = Column(Integer, ForeignKey('recording.id'), primary_key=True)
    comment_id = Column(Integer, ForeignKey('comment.id'), primary_key=True)
    op = Column(Boolean(name="op"))
    comment = relationship("Comment")

class CommentEventAssoc(Base):
    event_id = Column(Integer, ForeignKey('event.id'), primary_key=True)
    comment_id = Column(Integer, ForeignKey('comment.id'), primary_key=True)
    op = Column(Boolean(name="op"))
    comment = relationship("Comment")
