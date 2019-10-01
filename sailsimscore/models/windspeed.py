from .recordingdata import KNOTS_TO_M
from decimal import Decimal

class WindSpeedMixin(object):
    @property
    def windspeedknt(self):
        return (self.windspeed / KNOTS_TO_M).quantize(Decimal('1.00'))
    @windspeedknt.setter
    def windspeedknt(self, val):
        self.windspeed = val * KNOTS_TO_M
