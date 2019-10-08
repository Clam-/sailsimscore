import bcrypt
from enum import Enum as pyEnum
from ipaddress import ip_address
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    BINARY,
)

from .meta import Base
from .ip import IPMixin

class Role(pyEnum):
    admin = "A"
    user = "U"
    teamadmin = "T"

class User(IPMixin, Base):
    """ The SQLAlchemy declarative model class for a User object. """
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    _name = Column(Text, nullable=False, unique=True)
    role = Column(Enum(Role), nullable=False, name="role")
    email = Column(Text, unique=True)
    password_hash = Column(BINARY(60))

    def set_password(self, pw):
        self.password_hash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())

    def check_password(self, pw):
        if self.password_hash is not None:
            return bcrypt.checkpw(pw.encode('utf8'), self.password_hash)
        return False

    def isAdmin(self):
        return self.role and self.role is Role.admin

    @property
    def desc(self): return self.name

    def setEmail(self, email):
        return self.email = email.lower()

    def setName(self, name):
        self.name = name
        self._name = name.lower()
