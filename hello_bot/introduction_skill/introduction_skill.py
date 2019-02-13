from components.skills.base_skill import AbstractSkill

from introduction_skill.models.introduction_interaction import IntroductionInteraction


class IntroductionSkill(AbstractSkill):
    """
    Skill for managing Interactions about introduction form filling
    """

    def __init__(self, ic):
        self.ic = ic
        self.introduction_int = self.ic.im.get_or_create_instance_by_class(IntroductionInteraction)
