import django
from django.db import models

from components.matchers.matchers import TrainigPhrasesMatcher
from interactions.models import Interaction, AbstractInteraction, SendTextOperation, UserInteraction

from bank_interactions.models.slots import DesiredCurrencySlot


class GreetingInteraction(Interaction):
    """
    Says hello on start of dialog

    """

    # TODO translatable?
    out_text = "Здравствуйте, это помощник СберБанка"

    @classmethod
    def initialize(cls, ic, name=None, *args, **kwargs):
        # import ipdb; ipdb.set_trace()

        # intrctn = super(GreetingInteraction, cls).initialize(ic, name=name, *args, **kwargs)
        intrctn = super(GreetingInteraction, cls).initialize(ic, name=name, *args, **kwargs)
        # intrctn = super(Interaction, GreetingInteraction).initialize(ic, name=name, *args, **kwargs)

        # if not name:
        #     # default name is a name of class
        #     name = cls.__name__
        #
        # intrctn, _ = cls.objects.get_or_create(name=name)
        # intrctn.ic = ic
        # # TODO refactor to import base method of initilization and correctly use signals:
        # import ipdb; ipdb.set_trace()
        #
        # # Exit Signal Declaration
        # intrctn.exit_gate_signal = django.dispatch.dispatcher.Signal(providing_args=["userdialog"])

        # return intrctn
        # intrctn = cls()
        # intrctn = super(Interaction, intrctn).initialize(ic, name=None, *args, **kwargs)
        # # intrctn = Interaction.initialize(ic, name=None, *args, **kwargs)
        #
        intrctn.scenario = SendTextOperation(text=intrctn.out_text)
        # this Interaction may be activated by Receptor
        # TODO templatize
        intrctn.global_trigger_receptor = TrainigPhrasesMatcher(
            training_phrases=["Привет", "Здравствуйте", "Hello", "Kek", "Hi"],
            daemon_if_matched=intrctn.do)

        # here we connect the interaction's Global Receptors with InformationController's UserMessageEvent
        # (IC helps to adapt user-agnostic Interaction specification for particular User Case)
        ic.user_message_signal.connect(intrctn.global_trigger_receptor)
        return intrctn

    def connect_to_dataflow(self, ic):

        # deprecated

        self.ic = ic

        # self.exit_gate_signal = django.dispatch.Signal(providing_args=["userdialog"])

        ic.active_receptors.append(self.global_trigger_receptor)

    def do(self, *args, **kwargs):
        """
        What happens just after activation
        :return:
        """
        uint, created = UserInteraction.objects.get_or_create(userdialog=self.ic.userdialog, interaction=self)

        # print("hi_interaction.do")
        # actually send to chat
        # TODO make hypotheses queues?
        if uint.state == UserInteraction.COMPLETED:
            # we already greeted user
            # so skip his greeting
            return
        self.ic.userdialog.send_message_to_user(self.out_text)

        self.EXIT_GATES_SIGNALS[self.EXIT_GATE_OK].send(sender=self.__class__, userdialog=self.ic.userdialog)

        # import ipdb; ipdb.set_trace()
        # TODO refactor:
        # TODO send signal scenario completion
        uint.state = UserInteraction.COMPLETED
        uint.save()
        self.ic.user_message_signal.disconnect(self.global_trigger_receptor)
        return uint

    def start(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: Promise for completion?
        """
        return self.do(*args, **kwargs)


