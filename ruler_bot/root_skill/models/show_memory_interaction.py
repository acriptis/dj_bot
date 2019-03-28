from components.matchers.matchers import PhrasesMatcher
from components.interactions.models import Interaction
import json


class RestartUserDomainInteraction(Interaction):
    """When user restarts telegram bot we receive /start message we need to handle it as command
    for deleting data related to user"""
    def connect_to_dataflow(self, udc):
        """
        makes preparations fpor particular UserDomain. Here we may attach special receptors for
        VIP Users

        Args:
            udc: UserDomainController
        """

        #
        # ############### Prepare RECEPTOR #################################################
        # from components.receptors.models import Receptor
        # # from components.signal_reflex_routes.models.signals import ReceptorTriggeredSignal
        # receptor, created = Receptor.get_or_create(
        #     class_name='PhrasesMatcher', init_args={'phrases': ["/start"]})
        #
        # from components.signal_pattern_reflex.signal_pattern import SignalPattern
        # sp, _ = SignalPattern.get_or_create_strict(signal_type="UserMessageSignal")
        # udc.user_domain.user_message_signal_pattern.connect(receptor.__call__)
        #
        # receptor_trigger_signal_pattern, _ = SignalPattern.get_or_create_strict(
        #     signal_type="ReceptorTriggeredSignal", receptor=receptor)
        #
        # receptor_trigger_signal_pattern.connect(self.start)

        self._connect_receptor(receptor_type="PhrasesMatcher",
                               init_args={'phrases': ["/start"]},
                               callback_fn=self.start)

    def start(self, *args, **kwargs):
        # inits UserInteraction
        # super().start(*args, **kwargs)
        print(f"START interaction {self}")
        # load context:
        user_domain = kwargs['user_domain']
        # user_id = user_domain.user_id
        user_domain.udm.DialogPlanner.sendText(f"/start\nУдаляю данные для юзера: {user_domain.user_id}")

        user_domain.restart_userdomain()


class ShowMemoryInteraction(Interaction):
    """
    Interaction which responses with current memory state
    """

    def connect_to_dataflow(self, udc):
        """
        The post-initialize hook  for attaching global receptors.

        Here we connect the interaction's Global Receptors with InformationController
        :return:
        """
        # this Interaction may be activated by Receptor (actually it is binary intent classifier here)
        self.global_trigger_receptor = PhrasesMatcher(phrases=["slots", "слоты", "Memory"
                                                               ],
                                                      daemon_if_matched=self.start)
        # connect receptor:
        udc.user_message_signal.connect(self.global_trigger_receptor, weak=False)

        # self._prepare_slots()
        # # register slots:
        # # register LocationSlot with default value = Moscow
        # # register DateSlot with default value = now
        # # but slot processe must use following priorities for choosing the values:
        # # 1 if nothing provided use default slot value
        # # 2 if prehistory contains slot value choose preanswered slot value
        # # 3 as explicitly the value of slot for which case?
        # # register slots:

    def start(self, *args, **kwargs):
        data_raw = self.ic.MemoryManager.get_slots()
        print(data_raw)
        dict_to_json = json.dumps(data_raw, ensure_ascii=False, indent=2)
        print(dict_to_json)
        self.ic.DialogPlanner.sendText(dict_to_json)


class ShowAgendaInteraction(Interaction):
    """
    current agenda state
    """

    def post_init_hook(self):
        """
        The post-initialize hook  for attaching global receptors.

        Here we connect the interaction's Global Receptors with InformationController
        :return:
        """
        # this Interaction may be activated by Receptor (actually it is binary intent classifier here)
        self.global_trigger_receptor = PhrasesMatcher(phrases=["agenda", "план"
                                                               ],
                                                      daemon_if_matched=self.start)
        # connect receptor:
        self.ic.user_message_signal.connect(self.global_trigger_receptor, weak=False)

    def start(self, *args, **kwargs):
        data_raw = self.ic.DialogPlanner.agenda.queue_of_tasks
        print(data_raw)
        dict_to_json = json.dumps(str(data_raw), ensure_ascii=False, indent=2)
        print(dict_to_json)
        self.ic.DialogPlanner.sendText(dict_to_json)
