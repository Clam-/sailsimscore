from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from .meta import Base

class Boat(Base):
    """ The SQLAlchemy declarative model class for a Boat object. """
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    resource = Column(Text)

    @property
    def desc(self): return self.name
