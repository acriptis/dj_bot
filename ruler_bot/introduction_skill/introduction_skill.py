from introduction_skill.introduction_interaction import IntroductionInteraction


class IntroductionSkill():
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
        self.intro_int, _ = IntroductionInteraction.get_or_create()
        self.intro_int.connect_to_dataflow(self.udc)
