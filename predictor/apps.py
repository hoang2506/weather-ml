from django.apps import AppConfig


class PredictorConfig(AppConfig):
    name = "predictor"

class WeatherConfig(AppConfig):
    name = 'weather'
    model = None  # cache ở đây

    def ready(self):
        from .views import load_model
        WeatherConfig.model = load_model()
        print("Model loaded!")