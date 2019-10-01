from sqlalchemy import (
    Column,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .meta import Base
from .eventassoc import allowed_table

class Boat(Base):
    """ The SQLAlchemy declarative model class for a Boat object. """
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    resource = Column(Text)

    events = relationship("Event", secondary=allowed_table,
        back_populates="allowed_boats")

    @property
    def desc(self): return self.name
