from components.interactions.models import SlottyFormInteraction, Interaction
from components.slots.slots_factory import SlotsFactory


class IntroductionInteraction(Interaction):
    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        ### Slots Declaration #####################################################################
        # declarations which are agnostic to UserDomain:
        slots_factory = SlotsFactory()
        self.username_slot = slots_factory.produce_username_text_slot(
            'username_slot', "Дружок, как тебя зовут?")

        self.interests_slot = slots_factory.produce_categorical_slot(name='interests_slot',
                                                                     questioner="Какие у тебя хобби?",
                                                                     categories_domain_specification={
                                                                         "MOVIES": ["Кино",
                                                                                    "Фильм"],
                                                                         "MUSIC": ["Музык",
                                                                                   "Гитар"],
                                                                         "SPORT": ["Спорт",
                                                                                   "Кёрлинг",
                                                                                   "керлинг",
                                                                                   "Шахмат"],
                                                                         "BOOKS": ["Книги", "Чита"]
                                                                     })

        slots = [self.username_slot, self.interests_slot]
        name = "PrivateInfoSlottyForm"
        self.sfi = SlottyFormInteraction.make_slottfy_form(name, slots)

    def connect_to_dataflow(self, udc):
        """
        makes preparations fpor particular UserDomain. Here we may attach special receptors for
        VIP Users

        Args:
            udc: UserDomainController
        """
        self.ic = udc

        udc.sm.register_slot(self.username_slot)
        udc.sm.register_slot(self.interests_slot)
        # Connecting to dataflow
        self.sfi.connect_to_dataflow(udc)

        udc.im.register_interaction(self.sfi)
        # ############### Prepare RECEPTOR #################################################
        # ##################### System Connection (must be redone on system restart) #############
        from components.receptors.models import Receptor
        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        receptor, created = Receptor.get_or_create(
            class_name='PhrasesMatcher', init_args={'phrases': ["ПОЗНАКОМИМСЯ", "ЗНАКОМСТВО"]})

        sp, _ = SignalPattern.get_or_create_strict(signal_type="UserMessageSignal")
        udc.user_domain.user_message_signal_pattern.connect(receptor.__call__)
        receptor_trigger_signal_pattern, _ = SignalPattern.get_or_create_strict(
            signal_type="ReceptorTriggeredSignal", receptor=receptor)
        receptor_trigger_signal_pattern.connect(self.start)

    def start(self, *args, **kwargs):
        # inits UserInteraction
        super().start(*args, **kwargs)
        # load context:
        self.ic = kwargs['user_domain'].get_user_domain_controller()
        # self.ic.DialogPlanner.sendText("Начнем IntroductionInteraction")
        required_subinteraction_name = "PrivateInfoSlottyForm"
        self.ic.DialogPlanner.enqueue_interaction_by_name(required_subinteraction_name, priority=10)
        self.sfi = self.ic.im.get_or_create_instance_by_name(required_subinteraction_name)
        self.sfi.connect_exit_gate_with_fn(self.on_forma_filled)

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
        user_domain = kwargs['user_domain']
        udm = user_domain.udm

        username = udm.MemoryManager.get_slot_value_quite("username_slot")
        interests = udm.MemoryManager.get_slot_value_quite("interests_slot")
        self.make_recommendation(user_domain, username, interests)
        udm.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)

    def make_recommendation(self, user_domain, username, interests):
        """
        Method which implements recomendation from given arguments
        Args:
            user_domain: UserDomain
            username: name of the user
            interests: his interests

        Returns:

        """
        user_domain.udm.DialogPlanner.sendText(
            "Ок {username}, Я знаю что тебя интересуют {interests}".format(username=username, interests=interests))

        user_domain.udm.DialogPlanner.sendText(
            "Рекомендую тебе зубную пасту Colgate")
        pass
