from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self) -> None:      #this method gets called when the store app is ready
        import store.signals.handlers      #we are loading this module (the handler) when the app is ready