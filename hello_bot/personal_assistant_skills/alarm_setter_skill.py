from components.skills.base_skill import AbstractSkill
from personal_assistant_skills.models import AlarmSetterInteraction


class AlarmSkill(AbstractSkill):
    def __init__(self, ic):
        self.ic = ic
        self.alarm_setter_int = self.ic.im.get_or_create_instance_by_class(AlarmSetterInteraction)
