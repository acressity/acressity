'''
Helper functions that are used between various apps.
'''

import re
from urlparse import urlparse

from django.utils.html import escape
from django.conf import settings
from django.contrib.sites.models import Site


def embed_string(string):
    string = escape(string)  # Start by cleaning the thing out
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if re.search(pattern, string):
        urls = re.finditer(pattern, string)
        for url in urls:
            parsed_url = urlparse(url.group())
            if 'youtube' in parsed_url.netloc.lower():
                if 'v=' in parsed_url.query.lower():
                    code_start = re.search('v=', parsed_url.query).end()
                    if '&' in parsed_url.query:
                        # There is a secondary GET variable. Don't include that in the video assignment
                        code_end = parsed_url.query.find('&', re.search('v=', parsed_url.query).end())
                    else:
                        code_end = None
                    code = parsed_url.query[code_start:code_end]
                    string = string.replace(url.group(), '<div class="youtube"><iframe width="560" height="315" src="http://www.youtube.com/embed/{0}" frameborder="0" allowfullscreen></iframe></div>'.format(code))
            else:
                string = string.replace(url.group(), '<a href="{0}" target="blank">{0}</a>'.format(url.group()))
    return string

def build_full_absolute_url(absolute_url):
    return settings.SCHEME + '://' + Site.objects.get_current().domain + absolute_url
