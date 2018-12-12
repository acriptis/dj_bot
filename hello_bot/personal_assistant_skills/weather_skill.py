from components.skills.base_skill import AbstractSkill
from personal_assistant_skills.models import WeatherForecastInteraction


class WeatherSkill(AbstractSkill):
    """
    Skill for managing Interactions about weather forecast
    """

    def __init__(self, ic):
        self.ic = ic
        self.weather_int = self.ic.im.get_or_create_instance_by_class(WeatherForecastInteraction)
