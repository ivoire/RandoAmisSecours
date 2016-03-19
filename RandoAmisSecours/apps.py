from django.apps import AppConfig


class RASConfig(AppConfig):
    name = 'RandoAmisSecours'
    verbose_name = 'RandoAmisSecours'

    def ready(self):
        import RandoAmisSecours.receivers
