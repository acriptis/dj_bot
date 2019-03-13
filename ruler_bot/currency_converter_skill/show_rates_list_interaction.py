from components.interactions.models import Interaction
from components.slots.slots_factory import SlotsFactory


class ShowRatesListInteraction(Interaction):
    """
    Interaction responsible for detection of Intent to show rates of currencies
    and exposition of CurrencyService results into Dialog
    """

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        # construct model of receptors, slots and subinteractions
        # ####################################################################################
        # # Set up Intent Receptor ###############################################################
        from components.receptors.models import Receptor
        # from components.signal_reflex_routes.models.signals import ReceptorTriggeredSignal
        receptor, created = Receptor.get_or_create(
            class_name='PhrasesMatcher', init_args={'phrases': ["Курсы валют", "курсы"]})

        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        # pattern to connect for any user message (from any user domain)
        user_message_signal_pattern, _ = SignalPattern.get_or_create_strict(
            signal_type="UserMessageSignal")

        user_message_signal_pattern.connect(receptor.__call__)

        # set up triggering receptor:
        self.receptor_trigger_signal_pattern, _ = SignalPattern.get_or_create_strict(
            signal_type="ReceptorTriggeredSignal", receptor=receptor)


    #
    #
    #     # # Set up Currencies Receptor ###########################################################
    #     # slots_factory = SlotsFactory()
    #     # self.currencies_slot = slots_factory.produce_categorical_slot(name='currency_slot',
    #     #                                                               questioner="Какая валюта вас интересует?",
    #     #                                                               categories_domain_specification={
    #     #                                                                   "USD": ["доллар",
    #     #                                                                           "бакс"],
    #     #                                                                   "RUB": ["рубл",
    #     #                                                                           "руб"],
    #     #                                                                   "GBP": ["фунты",
    #     #                                                                           "фунт",
    #     #                                                                           "стерлинг"],
    #     #                                                                   "JPY": ["йены", "ен"],
    #     #                                                                   "EUR": ["евро"]
    #     #                                                               })

    def connect_to_dataflow(self, udc):
        """
        makes preparations for particular UserDomain. Here we may attach special receptors for
        VIP Users

        Args:
            udc: UserDomainController
        """
        # we should connect receptor trigger to interaction start because in init interaction
        # is not saved yet
        self.receptor_trigger_signal_pattern.connect(self.start)
        # import ipdb; ipdb.set_trace()


        # self.ic = udc
        #
        # ### Slots Declaration #####################################################################
        #         # declarations which are agnostic to UserDomain:
        # slots_factory = SlotsFactory()
        #
        # self.username_slot = slots_factory.produce_free_text_slot('username_slot', "Как вас зовут?")
        #
        # self.interests_slot = slots_factory.produce_categorical_slot(name='interests_slot',
        #                                                              questioner="Какие у вас хобби?",
        #                                                              categories_domain_specification={
        #                                                                  "MOVIES": ["Кино",
        #                                                                             "Фильм"],
        #                                                                  "MUSIC": ["Музык",
        #                                                                            "Гитар"],
        #                                                                  "SPORT": ["Спорт",
        #                                                                            "Кёрлинг",
        #                                                                            "Шахмат"],
        #                                                                  "BOOKS": ["Книги", "Чита"]
        #                                                              })
        #
        # slots = [self.username_slot, self.interests_slot]
        # # slots = [self.interests_slot, username_slot]
        # name = "PrivateInfoSlottyForm"
        # self.sfi = SlottyFormInteraction.make_slottfy_form(name, slots)
        #
        #
        # udc.sm.register_slot(self.username_slot)
        #
        #
        # udc.sm.register_slot(self.interests_slot)
        #
        # ########## Concrete FormFillingProcess Declaration/Initialization/ Registering:
        #
        # # slots = [self.username_slot, self.interests_slot]
        #
        # # name = "PrivateInfoSlottyForm"
        # #self.sfi = SlottyFormInteraction.make_slottfy_form(name, slots)
        #
        # # Connecting to dataflow
        # self.sfi.connect_to_dataflow(udc)
        #
        # udc.im.register_interaction(self.sfi)
        # #
        # # ############### Prepare RECEPTOR #################################################
        # # # this Interaction may be activated by Receptor (actually it is binary intent classifier here)
        # # self.global_trigger_receptor = PhrasesMatcher(phrases=["ПОЗНАКОМИМСЯ", "ЗНАКОМСТВО"],
        # #                                               daemon_if_matched=self.sfi.start)
        # # # TODO Receptor has intrification of connection. Is it BAD? How to restore it?
        # #
        # # ##################### System Connection (must be redone on system restart) #############
        # # # connect receptor:
        # # udc.receptors_pool.connect(self.global_trigger_receptor)
        # # # self.ic.user_message_signal.connect(self.global_trigger_receptor, weak=False)
        # # self.ic.DialogPlanner.sendText("Добро пожаловать в мир глубокого обучения!")
        #
        # from components.receptors.models import Receptor
        # # from components.signal_reflex_routes.models.signals import ReceptorTriggeredSignal
        # receptor, created = Receptor.get_or_create(
        #     class_name='PhrasesMatcher', init_args={'phrases': ["ПОЗНАКОМИМСЯ", "ЗНАКОМСТВО"]})
        #
        #
        # #udc.user_domain.user_message_signal.connect_receptor(receptor)
        # udc.user_domain.user_message_signal_pattern.connect(receptor.__call__)
        # from components.signal_pattern_reflex.signal import Signal
        # from components.signal_pattern_reflex.signal_pattern import SignalPattern
        # receptor_trigger_signal_pattern, _ = SignalPattern.get_or_create_strict(
        #     signal_type="ReceptorTriggeredSignal", user_domain=udc.user_domain, receptor=receptor)
        # # import ipdb; ipdb.set_trace()
        # #receptor_trigger_signal.connect_object_method(instance_locator=self, method_name='start')
        # receptor_trigger_signal_pattern.connect(self.start)
        pass

    def start(self, *args, **kwargs):
        """
        Show currency rates for RUB, USD, EUR, JPY

        Args:
            *args:
            **kwargs:

        Returns:

        """
        # super().start(*args, **kwargs)
        resulting_table_str = self._make_cur_rates_table()
        user_domain = kwargs['user_domain']
        udm = user_domain.udm
        udm.DialogPlanner.sendText(resulting_table_str)

    def _make_cur_rates_table(self, base_curr="RUB", currencies_codes=None):
        if not currencies_codes:
            currencies_codes = ["USD", "EUR", "JPY"]

        template_row = "1 %s -> %0.2f %s"
        from currency_converter import CurrencyConverter
        c = CurrencyConverter()
        resulting_text = "Курсы валют на сегодня:\n"
        for each_ref_cur in currencies_codes:
            base_amount = c.convert(1, each_ref_cur, base_curr)
            rate_line = template_row % (each_ref_cur, base_amount, base_curr)
            resulting_text += rate_line+"\n"

        return resulting_text

