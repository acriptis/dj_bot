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

        #self.udc.im.register_interaction(self.intro_int)
        self.intro_int.connect_to_dataflow(self.udc)

    # def process_step(self, message_str, user_id, state_obj):
    #     print("PROCESS STEP in Introduction Skill")
    #     import ipdb; ipdb.set_trace()
    #     print("PROCESS STEP in Introduction Skill")
    #     # super().process_step(message_str, user_id, state_obj)
