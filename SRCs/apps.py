from django.apps import AppConfig

class SRCsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SRCs'

    def ready(self):
        import SRCs.signals
