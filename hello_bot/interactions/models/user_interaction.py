from django.db import models
from .interactions import Interaction
from .userdialog import UserDialog

class UserInteraction(models.Model):
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
    # # user no user now)
    #
    INIT = 'Init'
    ACTIVE = 'Active'
    CANCELLED = 'Cancelled'
    COMPLETED = 'Completed'
    IGNORED = 'Ignored'
    INTERACTION_STATES = (
        (INIT, 'init'),
        (ACTIVE, 'Active'),
        (IGNORED, 'Ignored'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
    )

    state = models.CharField(
        max_length=2,
        choices=INTERACTION_STATES,
        default=INIT
    )

    userdialog = models.ForeignKey(UserDialog, on_delete=models.CASCADE)

    # def __init__(self, interaction, user, userdialog):
    #     self.interaction = interaction
    #     # if not status:
    #     #     status = self.INIT
    #     # self.status=status
    #
    #     # pointer to the node of latest_completed interaction of the graph:
    #     self.state_pointer=self.interaction.input_gate
    #     self.user=user
    #     self.state =
    #
    # def start_scenario_process(self, *args, **kwargs):
    #     """
    #     Input Gate is here
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     self.state = self.ACTIVE
    #     # what we return here?
    #     do_results_deferred = self.interaction.do(*args, **kwargs)
    #     # if done
    #     self.state = self.COMPLETED
    #     return do_results_deferred
    #
    # @classmethod
    # def activate(cls, interaction):
    #     uiprocess = UserInteraction(interaction=interaction,
    #                     # user=user,
    #                     state=UserInteraction.INIT
    #                     )
    #     return uiprocess
    #
    # @classmethod
    # def resume_or_init(self, interaction):
    #     # TODO
    #     pass
    #
    # def _resume(self):
    #     if self.state_pointer:
    #         # TODO multiouts?
    #         self.interaction.graph[self.state_pointer].out

