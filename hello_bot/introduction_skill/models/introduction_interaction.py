# -*- coding: utf-8 -*-
import django

from components.matchers.matchers import PhrasesMatcher
from interactions.models.forms_factory import SlottyFormInteraction

from interactions.models import Interaction
from components.slots.slots_factory import SlotsFactory


class IntroductionInteraction(Interaction):
# class IntroductionInteraction(AbstractInteraction):
    """
    Interaction which starts when user triggers trigger receptor on phrase cluster ПОЗНАКОМИМСЯ

    Interaction implements Form Filling Process with several slots, then launches recomendation step
    """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post_init_hook(self):
        """
        The post-initialize hook  for attaching global receptors.

        Here we connect the interaction's Global Receptors with InformationController
        :return:
        """
        ############### Prepare RECEPTOR #################################################
        # this Interaction may be activated by Receptor (actually it is binary intent classifier here)
        self.global_trigger_receptor = PhrasesMatcher(phrases=["ПОЗНАКОМИМСЯ", "ЗНАКОМСТВО", "/start"],
                                                      daemon_if_matched=self.start)
        # connect receptor:
        self.ic.user_message_signal.connect(self.global_trigger_receptor, weak=False)
        slots_factory = SlotsFactory()
        self.username_slot = slots_factory.produce_free_text_slot('username_slot', "Как тебя зовут?")
        self.ic.sm.register_slot(self.username_slot)

        self.interests_slot = slots_factory.produce_categorical_slot(name='interests_slot',
                                                                questioner="Какие имеешь увлечения?",
                                                                categories_domain_specification={
                                                                    "MOVIES": ["Кино", "Фильм"],
                                                                    "MUSIC": ["Музык", "Гитар"],
                                                                    "SPORT": ["Спорт", "Кёрлинг",
                                                                              "Шахмат"],
                                                                    "BOOKS": ["Книги", "Чита"]
                                                                })
        self.ic.sm.register_slot(self.interests_slot)

        ########## Concrete FormFillingProcess Declaration/Initialization/ Registering:
        name = "PrivateInfoSlottyForm2"
        slots = [self.username_slot, self.interests_slot]
        # slots = [self.interests_slot, username_slot]
        self.sfi = SlottyFormInteraction(name, slots)
        self.ic.im.register_interaction(self.sfi)

        #############################################################################################
        # TODO fix hardcode shit
        # initialize interaction:
        self.sfi.ic = self.ic
        self.sfi.EXIT_GATES_SIGNALS = {}

        if not hasattr(self.sfi, 'EXIT_GATES_NAMES_LIST'):
            # TODO fix to support inheritance of ExitGates!
            # then import default Gates :
            self.sfi.EXIT_GATES_NAMES_LIST = self.sfi.base_EXIT_GATES_NAMES_LIST

        # now init signal objects for each exit gate:
        for each_exit_gate_name in self.sfi.EXIT_GATES_NAMES_LIST:
            # create a signal object for each exit gate
            self.sfi.EXIT_GATES_SIGNALS[each_exit_gate_name] = django.dispatch.dispatcher.Signal(
                providing_args=["userdialog"])

        # self.sfi._anti_garbage_collector_callbacks_list = []
        # END ExitGate Signals Initialization


        self.sfi.post_init_hook()
        ########################################################################################


    def start(self, *args, **kwargs):
        """
        # if we here means we catched command to get weather forecast.
        # So we need to goalize slots of Location and Date
        # Both slots may have default values (or preloaded from user profile)
        # Both slots may be featured with confirmation interaction
        # Both Slots must be autofilled if user has specified the information before
        :param args:
        :param kwargs:
        :return:
        """
        # inits UserInteraction
        # super().start(*args, **kwargs)
        self.ic.DialogPlanner.enqueue_interaction(self.sfi, priority=10, callback_fn=self.on_forma_filled)
        print("self.ic.DialogPlanner.agenda.queue_of_tasks")
        print(self.ic.DialogPlanner.agenda.queue_of_tasks)
        # self.sfi.start(*args, **kwargs)
        # self.ic.im

    def on_forma_filled(self, *args, **kwargs):
        """
        When form is filled we should make a recomendation
        :param args:
        :param kwargs:
        :return:
        """
        # Recomendation Process:
        #
        # Describe slots filled
        # and make mock inference that this information makes the system to recommend some thing
        # import ipdb; ipdb.set_trace()
        print("KUKIKURUKIRUKIKU")
        username = self.ic.MemoryManager.get_slot_value_quite(self.username_slot.get_name())
        interests = self.ic.MemoryManager.get_slot_value_quite(self.interests_slot.get_name())
        self.make_recommendation(username, interests)
        self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)

    def make_recommendation(self, username, interests):
        """
        Method which implements recomendation from given arguments
        Args:
            username: name of the user
            interests: his interests

        Returns:

        """
        self.ic.DialogPlanner.sendText(
            "Ок {username}, Я знаю что тебя интересуют {interests}".format(username=username, interests=interests))

        self.ic.DialogPlanner.sendText(
            "Рекомендую тебе зубную пасту Colgate")
        pass