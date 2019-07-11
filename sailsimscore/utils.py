from ipaddress import ip_address
from pyramid_jinja2.filters import route_url_filter, static_url_filter
from jinja2 import Markup
from markdown import markdown
from os.path import relpath

def ip_disp(ip):
    return str(ip_address(ip))


def includeme(config):
    config.commit()
    jinjaenv = config.get_jinja2_environment()
    jinjaenv.filters['ip_disp'] = ip_disp
    jinjaenv.filters['route_url'] = route_url_filter
    jinjaenv.filters['static_url'] = static_url_filter
    jinjaenv.filters['markdown'] = lambda text: Markup(markdown(text, output_format="html5"))

    #download link maker
    approot = config.get_settings()['approot']
    jinjaenv.filters['downURL'] = \
        lambda path: "sailsimscore:../{0}".format(relpath(path, approot))
