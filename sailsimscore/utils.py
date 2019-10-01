from ipaddress import ip_address
from pyramid_jinja2.filters import route_url_filter, static_url_filter
from jinja2 import Markup
from markdown import markdown
from os.path import join
from .models.recordingdata import Course, Gusts

def ip_disp(ip):
    return str(ip_address(ip))


def includeme(config):
    config.commit()
    jinjaenv = config.get_jinja2_environment()
    jinjaenv.trim_blocks = True
#    jinjaenv.lstrip_blocks = True
    jinjaenv.filters['ip_disp'] = ip_disp
    jinjaenv.filters['route_url'] = route_url_filter
    jinjaenv.filters['static_url'] = static_url_filter
    jinjaenv.filters['markdown'] = \
        lambda text: Markup(markdown(text, output_format="html5")) if text else ""

    #download link maker
    prefix = config.get_settings()['recordingprefix']
    jinjaenv.filters['downURL'] = lambda path: join(prefix, path)
    jinjaenv.filters['dtiso'] = lambda dt: dt.isoformat()
    # Add recording Enums to scope
    jinjaenv.globals["Course"] = Course
    jinjaenv.globals["Gusts"] = Gusts
