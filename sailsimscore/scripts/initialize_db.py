import argparse
import sys

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.exc import OperationalError

from .. import models

BOAT_LIST = [
    ("Laser Standard", 7000),
    ("Laser Radial", 7002),
    ("Laser 4.7", 7003),
    ("Byte", 1001),
    ("Opti", 1002),
    ("Megabyte", 1011),
    ("Liberty", 1012),
    ("Liberty Motor", 1013),
    ("29er", 1014),
]

def setup_models(dbsession):
    """
    Add or update models / fixtures in the database.

    """
    root = models.user.User(name='admin', email='admin', role=models.user.Role.admin)
    root.set_password("sailsimscore")
    dbsession.add(root)
    # Add boats
    for boat, num in BOAT_LIST:
        b = models.boat.Boat()
        b.id = num
        b.name = boat
        dbsession.add(b)

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config_uri',
        help='Configuration file, e.g., development.ini',
    )
    return parser.parse_args(argv[1:])


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)

    try:
        with env['request'].tm:
            dbsession = env['request'].dbsession
            setup_models(dbsession)
    except OperationalError:
        print('''
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to initialize your database tables with `alembic`.
    Check your README.txt for description and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.
            ''')
