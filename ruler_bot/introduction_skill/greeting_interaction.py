# -*- coding: utf-8 -*-
from components.matchers.matchers import PhrasesMatcher
from components.interactions.models import Interaction


class GreetingInteraction(Interaction):
    """
    Says hello on start of dialog

    """

    # TODO translatable?
    out_text = "Привет, только дураки ничего не боятся, нормальные пацаны всегда занижают  "

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

    def connect_to_dataflow(self, udc):
        """
        makes preparations fpor particular UserDomain. Here we may attach special receptors for
        VIP Users

        Args:
            udc: UserDomainController
        """

        # ############### Prepare RECEPTOR #################################################
        # # this Interaction may be activated by Receptor (actually it is binary intent classifier here)
        # self.global_trigger_receptor = PhrasesMatcher(phrases=["ПОЗНАКОМИМСЯ", "ЗНАКОМСТВО"],
        #                                               daemon_if_matched=self.sfi.start)
        # # TODO Receptor has intrification of connection. Is it BAD? How to restore it?
        #
        # ##################### System Connection (must be redone on system restart) #############
        # # connect receptor:
        # udc.receptors_pool.connect(self.global_trigger_receptor)
        # # self.ic.user_message_signal.connect(self.global_trigger_receptor, weak=False)
        # self.ic.DialogPlanner.sendText("Добро пожаловать в мир глубокого обучения!")

        from components.receptors.models import Receptor
        # from components.signal_reflex_routes.models.signals import ReceptorTriggeredSignal
        receptor, created = Receptor.get_or_create(
            class_name='PhrasesMatcher',
            init_args={'phrases': ["Привет", "Здравствуйте", "Hello", "Kek", "Hi", "Приветик"]})


        #udc.user_domain.user_message_signal.connect_receptor(receptor)
        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        sp, _ = SignalPattern.get_or_create_strict(signal_type="UserMessageSignal")
        udc.user_domain.user_message_signal_pattern.connect(receptor.__call__)
        # udc.user_domain.user_message_signal_pattern.connect(receptor.__call__)
        from components.signal_pattern_reflex.signal import Signal
        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        receptor_trigger_signal_pattern, _ = SignalPattern.get_or_create_strict(
            signal_type="ReceptorTriggeredSignal", receptor=receptor)
        # import ipdb; ipdb.set_trace()
        #receptor_trigger_signal.connect_object_method(instance_locator=self, method_name='start')
        receptor_trigger_signal_pattern.connect(self.start)

    def start(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: Promise for completion?
        """
        # check that we have not been greeting already
        self.ic.DialogPlanner.sendText("Привет, говоришь")
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

