from components.skills.base_skill import AbstractSkill


from root_skill.models import ShowMemoryInteraction, ShowAgendaInteraction


class RootSkill(AbstractSkill):
    """
    Skill for managing Interactions about weather forecast
    """

    def __init__(self, ic):
        self.ic = ic
        self.show_memory = self.ic.im.get_or_create_instance_by_class(ShowMemoryInteraction)
        self.show_agenda = self.ic.im.get_or_create_instance_by_class(ShowAgendaInteraction)

