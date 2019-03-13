from introduction_skill.introduction_interaction import IntroductionInteraction
from translator_skill.translate_interaction import TranslatorInteraction


class TranslatorSkill():
    def connect_to_dataflow(self, user_domain_controller):
        """
        Method which prepares stae of the skill for particular UserDomain

        This method used for attaching (persistent) receptors into runtime system

        Args:
            user_domain_controller:

        Returns:

        """
        print("connect_to_dataflow!")
        self.udc = user_domain_controller

        # base interactions and scenario linking:
        self.translator_int, _ = TranslatorInteraction.get_or_create()

        #self.udc.im.register_interaction(self.intro_int)
        self.translator_int.connect_to_dataflow(self.udc)
