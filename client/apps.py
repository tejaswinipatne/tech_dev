from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ClientConfig(AppConfig):
    name = 'client'
    verbose_name = _('profiles')

    def ready(self):
        import client.signals
