from enum import Enum as pyEnum

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
