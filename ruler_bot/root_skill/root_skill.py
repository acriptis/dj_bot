
from root_skill.models import ShowMemoryInteraction, ShowAgendaInteraction, RestartUserDomainInteraction


class RootSkill():
    """
    Skill for managing Interactions about weather forecast
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

        self.userdomain_reset, _ = RestartUserDomainInteraction.get_or_create()
        self.userdomain_reset.connect_to_dataflow(self.udc)

        # self.show_memory, _ = ShowMemoryInteraction.get_or_create()
        # self.show_memory.connect_to_dataflow(self.udc)
        #
        # self.show_agenda, _ = ShowAgendaInteraction.get_or_create()
        # self.show_agenda.connect_to_dataflow(self.udc)

