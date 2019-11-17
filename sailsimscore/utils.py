from ipaddress import ip_address
from pyramid_jinja2.filters import route_url_filter, static_url_filter
from jinja2 import Markup
from markdown import markdown, Markdown
from os.path import join
from .models.recordingdata import Course, Gusts
from io import StringIO

def ip_disp(ip):
    return str(ip_address(ip))

# From: https://stackoverflow.com/a/54923798
def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()

# patching Markdown
Markdown.output_formats["plain"] = unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False
def unmark(text):
    return __md.convert(text)

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
    jinjaenv.filters['plaindown'] = \
        lambda text: Markup(unmark(text)) if text else ""
    jinjaenv.filters['dtiso'] = lambda dt: dt.isoformat()
    # Add recording Enums to scope
    jinjaenv.globals["Course"] = Course
    jinjaenv.globals["Gusts"] = Gusts
