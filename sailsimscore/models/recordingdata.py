from enum import Enum as pyEnum
from decimal import Decimal

# Make sure if modifying these constants to modify them in the templates
class Course(pyEnum):
    none = 0
    CrossWind = 1
    Trapezoidal = 2
    Triangular = 3
    UpDownWind = 4

class Gusts(pyEnum):
    none = 0
    random = 1000
    repeat = 1001
    any = -1

KNOTS_TO_M = Decimal("0.5144")
M_TO_KNOTS = Decimal("1.9438") #This doesn't quite line up? Divide above instead.
