from components.matchers.matchers import PhrasesMatcher
from interactions.models import Interaction, AbstractInteraction, SendTextOperation, UserInteraction


class GreetingInteraction(Interaction, AbstractInteraction):
    """
    Says hello on start of dialog

    """

    # TODO translatable?
    out_text = "Здравствуйте, это помощник Банка"

    def post_init_hook(self):

        # self.exit_gate_signal = django.dispatch.Signal(providing_args=["userdialog"])

        # ic.active_receptors.append(self.global_trigger_receptor)
        self.scenario = SendTextOperation(text=self.out_text)
        # this Interaction may be activated by Receptor
        # TODO templatize
        self.global_trigger_receptor = PhrasesMatcher(
            phrases=["Привет", "Здравствуйте", "Hello", "Kek", "Hi", "Приветик", "БАНК", "КОНСУЛЬТАЦИЯ"],
            daemon_if_matched=self.start)

        # here we connect the interaction's Global Receptors with InformationController's UserMessageEvent
        # (IC helps to adapt user-agnostic Interaction specification for particular User Case)
        self.ic.user_message_signal.connect(self.global_trigger_receptor, weak=False)

    def start(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: Promise for completion?
        """
        # super(self.__class__, self).start(*args, **kwargs)
        # TODO refactor
        # greeting interaction makes explicit check of UserInteraction state to handle start behaviour, so we
        # can not just call super method (or we need to request UserInteraction instance again in child method)
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

