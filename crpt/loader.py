from os.path import dirname, join, abspath, isdir

from django.template.loader import BaseLoader
from django.db.models import get_app
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.conf import settings
from django.utils._os import safe_join

class Loader(BaseLoader):
    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):
        app_name, template_name = template_name.split(":", 1)
        try:
            template_dir = abspath(safe_join(dirname(get_app(app_name).__file__), 'templates'))
        except ImproperlyConfigured:
            raise TemplateDoesNotExist()

        return template_name, template_dir

    def load_template_source(self, template_name, template_dirs=None):
        """
        Template loader that only serves templates from specific app's template directory.

        Works for template_names in format app_label:some/template/name.html
        """
        if ":" not in template_name:
            raise TemplateDoesNotExist()

        template_name, template_dir = self.get_template_sources(template_name)

        if not isdir(template_dir):
            raise TemplateDoesNotExist()

        filepath = safe_join(template_dir, template_name)
        with open(filepath, 'rb') as fp:
            return (fp.read().decode(settings.FILE_CHARSET), filepath)


    load_template_source.is_usable = True
