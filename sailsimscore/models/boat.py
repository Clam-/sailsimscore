from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from .meta import Base

class Boat(Base):
    """ The SQLAlchemy declarative model class for a Boat object. """
    __tablename__ = 'boats'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    resource = Column(Text)
