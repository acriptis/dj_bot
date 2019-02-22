from components.matchers.matchers import PhrasesMatcher
from interactions.models import Interaction, AbstractInteraction
import django.dispatch
import json


class ShowMemoryInteraction(Interaction, AbstractInteraction):
    """
    Interaction which responses with current memory state
    """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)
        super(AbstractInteraction, self).__init__()

    def post_init_hook(self):
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
        self.ic.user_message_signal.connect(self.global_trigger_receptor, weak=False)

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


class ShowAgendaInteraction(Interaction, AbstractInteraction):
    """
    current agenda state
    """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)
        super(AbstractInteraction, self).__init__()

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
#
# class ActiveUserProcesses(Interaction, AbstractInteraction):
#     """
#     current agenda state
#     """
#     class Meta:
#         proxy = True
#
#     def __init__(self, *args, **kwargs):
#         super(Interaction, self).__init__(*args, **kwargs)
#         super(AbstractInteraction, self).__init__()
#
#     def post_init_hook(self):
#         """
#         The post-initialize hook  for attaching global receptors.
#
#         Here we connect the interaction's Global Receptors with InformationController
#         :return:
#         """
#         # this Interaction may be activated by Receptor (actually it is binary intent classifier here)
#         self.global_trigger_receptor = TrainigPhrasesMatcher(training_phrases=["agenda", "план"
#                                                                                   ],
#                                                                 daemon_if_matched=self.start)
#         # connect receptor:
#         self.ic.user_message_signal.connect(self.global_trigger_receptor, weak=False)
#
#     def start(self, *args, **kwargs):
#         data_raw = self.ic.DialogPlanner.agenda.queue_of_tasks
#         print(data_raw)
#         dict_to_json = json.dumps(data_raw, ensure_ascii=False, indent=2)
#         print(dict_to_json)
#         self.ic.DialogPlanner.sendText(dict_to_json)