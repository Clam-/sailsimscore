from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean
)

from .meta import Base

class CommentAssociation(Base):
    __tablename__ = 'reccomments'
    recording_id = Column(Integer, ForeignKey('recordings.id'), primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.id'), primary_key=True)
    op = Column(Boolean)
    comment = relationship("Comment")
