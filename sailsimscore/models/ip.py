from ipaddress import ip_address
from sqlalchemy import (
    Column,
    BINARY,
)
class IPMixin(object):
    _createdip = Column(BINARY(16))
    _modip = Column(BINARY(16))
    @property
    def createdip(self): return str(ip_address(self._createdip)) if self._createdip else None
    @createdip.setter
    def createdip(self, value): self._createdip = ip_address(value).packed
    @property
    def modip(self): return str(ip_address(self._modip))  if self._modip else None
    @modip.setter
    def modip(self, value): self._modip = ip_address(value).packed
