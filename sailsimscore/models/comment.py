from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship

from .meta import Base

class Comment(Base):
    """ The SQLAlchemy declarative model class for a Comment object. """
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(Text)

    user_id = Column(ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref='comments')

class CommentAssociation(Base):
    __tablename__ = 'reccomments'
    recording_id = Column(Integer, ForeignKey('recordings.id'), primary_key=True)
    comment_id = Column(Integer, ForeignKey('comments.id'), primary_key=True)
    op = Column(Boolean)
    comment = relationship("Comment")
