# from introduction_skill.introduction_interaction import IntroductionInteraction
from currency_converter_skill.show_rates_list_interaction import ShowRatesListInteraction


class CurrencyConverterSkill():
    """Skill which can help with currency rates conversion

    """
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
        self.show_rates_int, _ = ShowRatesListInteraction.get_or_create()

        #self.udc.im.register_interaction(self.intro_int)
        self.show_rates_int.connect_to_dataflow(self.udc)
