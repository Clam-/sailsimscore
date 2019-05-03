from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from .meta import Base

class Comment(Base):
    """ The SQLAlchemy declarative model class for a Comment object. """
    __tablename__ = 'boats'
    id = Column(Integer, primary_key=True)
    content = Column(Text)

    user_id = Column(ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref='comments')
