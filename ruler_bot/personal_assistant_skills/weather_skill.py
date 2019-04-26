# from components.skills.base_skill import AbstractSkill
from personal_assistant_skills.models import WeatherForecastInteraction


class WeatherSkill():
    """
    Skill for managing Interactions about weather forecast
    """

    def __init__(self):
        self.weather_int, _ = WeatherForecastInteraction.get_or_create()

    def connect_to_dataflow(self, udm):
        self.weather_int.connect_to_dataflow(udm)
