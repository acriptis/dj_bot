from personal_assistant_skills.models import AlarmSetterInteraction


class AlarmSkill():

    def __init__(self):
        self.alarm_int, _ = AlarmSetterInteraction.get_or_create()

    def connect_to_dataflow(self, udm):
        self.alarm_int.connect_to_dataflow(udm)
