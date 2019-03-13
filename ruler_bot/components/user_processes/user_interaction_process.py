from mongoengine import ReferenceField
from mongoengine.queryset.base import CASCADE

from components.user_processes.user_process import UserProcess
from components.interactions.models.interactions import Interaction


class UserInteractionProcess(UserProcess):
    interaction = ReferenceField(Interaction, reverse_delete_rule=CASCADE)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        # create signal for each exit gate in interaction
        # Exit Gate Signals and Registry initialization
        self.EXIT_GATES_SIGNALS = {}

        if not hasattr(self.interaction, 'EXIT_GATES_NAMES_LIST'):
            # TODO fix to support inheritance of ExitGates!
            # then import default Gates :
            self.EXIT_GATES_NAMES_LIST = self.interaction.base_EXIT_GATES_NAMES_LIST
        else:

            self.EXIT_GATES_NAMES_LIST = self.interaction.EXIT_GATES_NAMES_LIST

        # now init signal objects for each exit gate:
        # from components.signal_reflex_routes.models.signals import InteractionProcessCompletedSignal
        from components.signal_pattern_reflex.signal import Signal

        for each_exit_gate_name in self.EXIT_GATES_NAMES_LIST:
           # create a signal object for each exit gate
           # self.EXIT_GATES_SIGNALS[each_exit_gate_name] =
           # django.dispatch.dispatcher.Signal(providing_args=["userdialog"])
           self.EXIT_GATES_SIGNALS[each_exit_gate_name] = Signal(
               signal_type="InteractionProcessCompletedSignal", user_domain=self.user_domain,
                                                               interaction=self.interaction,
                                                               exit_gate=each_exit_gate_name)
               # InteractionProcessCompletedSignal.get_or_create(user_domain=self.user_domain,
               #                                                 interaction=self.interaction,
               #                                                 exit_gate=each_exit_gate_name)


    def __str__(self):
        return "UserInteractionProcess: User:<%s> Interaction: %s" % (
            self.user_domain.dialog.get_target_user(), self.interaction)
