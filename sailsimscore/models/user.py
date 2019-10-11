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
from sqlalchemy.ext.hybrid import hybrid_property

from .meta import Base
from .ip import IPMixin

class Role(pyEnum):
    admin = "A"
    user = "U"
    teamadmin = "T"

class User(IPMixin, Base):
    """ The SQLAlchemy declarative model class for a User object. """
    id = Column(Integer, primary_key=True)
    _name = Column('name', Text, nullable=False)
    _name_unique = Column('name_unique', Text, nullable=False, unique=True)
    role = Column(Enum(Role), nullable=False, name="role")
    _email = Column('email', Text, unique=True)
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

    @hybrid_property
    def email(self):
        return self._email
    @email.setter
    def email(self, em):
        self._email = em.lower()

    @hybrid_property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name
        self._name_unique = name.lower()
