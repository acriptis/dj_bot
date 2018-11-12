# coding=utf-8
from interactions.models import Interaction, AbstractInteraction, SendTextOperation, UserInteraction
from bank_interactions.models.slots import DesiredCurrencySlot, OptionIntentsSlot, NeedListDocsAndTarifsSlot, \
    ClientIsResidentRFSlot, ClientServiceRegionSlot, ClientPropertyTypeSlot, ClientAgreeWithServicePackConditionsSlot


class IntentRetrievalInteraction(Interaction, AbstractInteraction):
    """
    retrieves asks question user for his goal

    and classifies answers into exit gates of different intents

    # TODO
    exit gates or productions signals:
    """

    # external slots defined somewhere
    required_slots = [OptionIntentsSlot]

    class Meta:
        proxy = True

    # def __init__(self, ic, name='intent_retrieval_interaction', *args, **kwargs):
    #     super(Interaction, self).__init__(*args, **kwargs)
    #     super(AbstractInteractionSignalingExit, self).__init__(*args, **kwargs)
    # TODO move to Interactions Model abstraction:
    # @classmethod
    # def initialize(cls, ic, name=None, *args, **kwargs):
    #     if not name:
    #         # default name is a name of class
    #         name = cls.__name__
    #
    #     intrctn, _ = cls.objects.get_or_create(name=name)
    #     intrctn.ic = ic
    #     super(AbstractInteraction, intrctn).__init__(*args, **kwargs)
    #
    #     return intrctn

    def start(self, *args, **kwargs):
        super(self.__class__, self).start(*args, **kwargs)
        # 1. retrieve OptionIntentsSlot
        self.ic.DialogPlanner.plan_process_retrieve_slot_value(OptionIntentsSlot, callback_fn=self.on_intents_ready)

        # TODO consider
        # how to handle MultiGateness:
        #1. emit signal of productions (requires DialogPlanner to be responsible
        # for linking control pass to further Interactions)
        #2. direct requesting interactions by name (absorbs knowledge about transition into
        # self object)
        # What is better depends on size of Rule Base and practice of modification
        # of the Solution Project.

    def on_intents_ready(self, *args, **kwargs):
        # disconnect signal

        ######################### Busines Rule BR1.1 Block ##########################################
        # implemented as functional component
        # if implement as class object then it must be listening to OptionIntentsSlot slot_filled signal
        print("INTENTS READY")

        # TODO wrap it into better code snippet!
        intents_opts = kwargs['user_slot_process'].result.value
        intents_opts = self.ic.MemoryManager.put_slot_value(OptionIntentsSlot.name, intents_opts)

        def check_rule_1_1_INTENTER(intents_opts):

            if not intents_opts:
                # Exception Scneario, requestioning strategy?
                return False
            elif OptionIntentsSlot.COMMON_INFO in intents_opts:
                return True
            elif OptionIntentsSlot.SECRET_INFO in intents_opts:
                return True
            else:
                raise Exception("Unknown intents: %s!" % intents_opts)

        def action_rule_1_1_INTENTER():
            """
            Here we merge 2 atomic business rulescheck_rule_1_1_INTENTER

            We can make direct call of currencies interaction

            :return:
            """
            # import ipdb; ipdb.set_trace()

            if OptionIntentsSlot.COMMON_INFO in intents_opts:
                self.ic.DialogPlanner.enqueue_interaction_by_name("DesiredCurrencyInteraction", priority=10)
                self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)

            if OptionIntentsSlot.SECRET_INFO in intents_opts:
                self.ic.DialogPlanner.enqueue_interaction_by_name("BusinessOfferingInteraction", priority=1)
                # TODO generally it better to check if this interaction is not completed yet:
                self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)

        if check_rule_1_1_INTENTER(intents_opts):
            action_rule_1_1_INTENTER()
        else:
            # Exception Scenario
            print("Exception Scenario?")
        ######################### END Busines Rule BR2.1 Block ##########################################

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return self.__class__.__name__


class DesiredCurrencyInteraction(Interaction, AbstractInteraction):
    """
    В какой валюте Клиент желает открыть счет?
        Если в рублях, перейди к шагу 3
        Если в ин. валюте, проверь возможность открытия счета в ин. валюте, названной Клиентом, на сайте в разделе Расчетно-кассовое обслуживание.
            Иные документы, перейди к шагу 3

    asks the currency of the account to be opened

    Does logic of Handling NONRUB case

    uses
        DesiredCurrencySlot.name

    produces
        value of DesiredCurrencySlot
            (may be a list)

    exit gates:
    1. RUB
    2. OtherCurrency

    """
    #sc_graph = Graph()
    #sc_graph.node['start'].then('greeting', schema=GreetingInteraction)
    #sc_graph.node['greeting'].then('desired_currency', schema=SlotProcess(DesiredCurrencySlot))
    #
    #sc_graph.node['desired_currency'].then("currencies_switch", schema=SWITCH(sc_graph))
    #sc_graph.node['currencies_switch'].if_then('desired_currency(NONRUB)', 'sendText2.1')
    #sc_graph.node['currencies_switch'].if_then('desired_currency(NONRUB)', 'sendText2.1')
    #
    #
    #sc_graph.node['sendText2.1'].requires(SendText("Hehehe Text2.1"))
    #
    #
    #
    ## , SWITCHER, products = ['desired_currency(RUB)', 'desired_currency(NONRUB)'])
    #scenario = {
    #    'start': GreetingInteraction,
    #    # 'fin': completion condition? Rules
    #}
    TEXT_2_1 = "Текст 2.1 про то как быть с нерублевыми валютами"

    EXIT_GATE_EXCEPTION = "Oops, Exception"

    class Meta:
        proxy = True

    # def __init__(self, ic, name='desired_currency_interaction',*args, **kwargs):
    #     super(Interaction, self).__init__(*args, **kwargs)
    #     super(AbstractInteractionSignalingExit, self).__init__(*args, **kwargs)
    #     self.ic = ic
    #     self.name = name

    # @classmethod
    # def initialize(cls, ic, name=None, *args, **kwargs):
    #     if not name:
    #         # default name is a name of class
    #         name = cls.__name__
    #
    #     intrctn, _ = cls.objects.get_or_create(name=name)
    #     intrctn.ic = ic
    #     super(AbstractInteraction, intrctn).__init__(*args, **kwargs)
    #
    #     return intrctn

    def start(self, *args, **kwargs):
        print("DesiredCurrencyInteraction.start(")
        super(self.__class__, self).start(*args, **kwargs)
        # 1. retrieve CurrencySlot
        self.ic.DialogPlanner.plan_process_retrieve_slot_value(DesiredCurrencySlot, callback_fn=self.on_desired_currency_ready)

    def on_desired_currency_ready(self, *args, **kwargs):
        """
        event handler which
        triggers rule checks
        and precompletion behaviour
        before completing the state of the interaction
        """
        print("DesiredCurrencyInteraction.on_desired_currency_ready(")
        # desired_currency_values = self.ic.MemoryManager.get_slot_value(DesiredCurrencySlot.name)
        desired_currency_values = kwargs['user_slot_process'].result.value
        desired_currency_values = self.ic.MemoryManager.put_slot_value(DesiredCurrencySlot.name,
                                                                       desired_currency_values)

        ######################### Busines Rule BR2.1 Block ##########################################
        # implemented as functional component
        # if implement as class object then it must be listening to DesiredCurrencySlot slot_filled signal

        # given a filled slot of currency it routes result into two production classes:
        #      - RUB
        #      - NONRUBS (EUR, USD etc)
        #
        #     It may be done with ontology retrieval mechanics or as hard coded rule base (AS-IS :) )
        def check_rule_2_1_NONRUB(currency_code):
            if currency_code != DesiredCurrencySlot.RUB:
                return True
            else:
                return False

        def action_rule_2_1_NONRUB():
            self.ic.DialogPlanner.sendText(self.TEXT_2_1)

        ###################################################
        if isinstance(desired_currency_values, list):
            # special Case for multiple currencies
            nonrub_currencies = list(filter(check_rule_2_1_NONRUB, desired_currency_values))
            if nonrub_currencies:
                action_rule_2_1_NONRUB()
        else:
            raise Exception("Unexpect datatype for desired_currency_values: %s, %s" % (desired_currency_values, type(desired_currency_values)))

        ######################### END Busines Rule BR2.1 Block ##########################################

        # Completion can be announced
        self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)


class DocumentsListSupplyInteraction(Interaction, AbstractInteraction):
    """
    3.

    Спроси у Клиента, интересует ли его перечень документов для открытия счета и тарифы на открытие и обслуживание счета?

    Если ДА,
        уточни у Клиента, является ли он резидентом РФ, форму собственности и регион обслуживания.
        проинформируй Клиента о действующих спец. предложениях:
        спец. предложение для ЮЛ - Клиентов сторонних банков, у которых отозваны лицензии на осуществление банковской деятельности (см.п.9.5 документа Расчетно-кассовое обслуживание);
        спец. предложение для открытия расчетного счета корпоративным Клиентам (см. документ Расчетно-кассовое обслуживание).

        Перейди к шагу 4

    Если НЕТ, счет в рублях, перейди к шагу 6
    Если НЕТ, счет в ин.валюте, перейди к шагу 7
    """

    # message to user after the PrivateInfoForm is filled
    TEXT_3_docs_list_info = """
       Действующие спец. предложения:

       -спец. предложение для ЮЛ - Клиентов сторонних банков, 
       у которых отозваны лицензии на 
       осуществление банковской деятельности 
       (см.п.9.5 документа Расчетно-кассовое обслуживание);

       -спец. предложение для открытия расчетного счета
       корпоративным Клиентам (см. документ Расчетно-кассовое обслуживание). 
       """

    EXIT_GATE_3_1 = "ExitGate3.1"
    EXIT_GATE_3_2_RUB = "ExitGate3.2.RUB"
    EXIT_GATE_3_2_NONRUB= "ExitGate3.2.NonRUB"

    # Custom exit gates must be declared explicitly
    EXIT_GATES_NAMES_LIST = [
        EXIT_GATE_3_1,
        EXIT_GATE_3_2_RUB,
        EXIT_GATE_3_2_NONRUB
    ]

    def start(self, *args, **kwargs):
        # 1. retrieve CurrencySlot
        print("Ready to go: DocumentsListSupplyInteraction.start")
        super(self.__class__, self).start(*args, **kwargs)
        uip = self.ic.DialogPlanner.initialize_user_interaction_proc(self)
        # 1. retrieve CurrencySlot
        self.ic.DialogPlanner.plan_process_retrieve_slot_value(NeedListDocsAndTarifsSlot,
                                                               callback_fn=self.on_response_3_Q1_ready)
    # @classmethod
    # def initialize(cls, ic, name=None, *args, **kwargs):
    #     super(DocumentsListSupplyInteraction, cls).do(a)

    def on_response_3_Q1_ready(self, *args, **kwargs):
        """
        See step 3.Q1 at
        https://www.draw.io/?state=%7B%22ids%22:%5B%221kbtHH-S2G1QbnZM_tuo6KR4RxcMrbu1h%22%5D,%22action%22:%22open%22,%22userId%22:%22110709776902094243429%22%7D#G1kbtHH-S2G1QbnZM_tuo6KR4RxcMrbu1h
        :param args:
        :param kwargs:
        :return:
        """
        needs_tarifs_and_docs = kwargs['user_slot_process'].result.value
        needs_tarifs_and_docs = self.ic.MemoryManager.put_slot_value(NeedListDocsAndTarifsSlot.name,
                                                                     needs_tarifs_and_docs)
        print(needs_tarifs_and_docs)
        print("on_response_3_Q1_ready method")
        if NeedListDocsAndTarifsSlot.ANSWER_YES in needs_tarifs_and_docs:
            print("kekekuku")
            # following interaction encapsulates:
            #     plan Form Filling process,
            #       on completed Send Text
            #     then complete self
            self.ic.DialogPlanner.enqueue_interaction_by_name("PrivateInfoFormInteraction",
                                                              callback_fn=self.on_private_info_form_completed)

        elif NeedListDocsAndTarifsSlot.ANSWER_NO in needs_tarifs_and_docs:

            # assering existence of variable's value:
            desired_currency_slot_value = self.ic.MemoryManager.get_slot_value(DesiredCurrencySlot.name)
            # TODO more general solution is recommended:
            if DesiredCurrencySlot.RUB in desired_currency_slot_value:
                # step 6
                self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_3_2_RUB)
                pass
            else:
                # step 7
                self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_3_2_NONRUB)
                pass
            # Проверка неточно отражает логику сценария. Возможны случаи когда клиент упомянул две и более валюты
            # рублевую и нерублевую, в этом случае поведение не определено однозначно

    def on_private_info_form_completed(self, *args, **kwargs):
        #
        """
        When Private Info form is filled we need to send text 3.docs_list.inform
        :param args:
        :param kwargs:
        :return:
        """
        self.ic.DialogPlanner.sendText(self.TEXT_3_docs_list_info)

        # then we may announce completion by ExitGate3.1
        self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_3_1)


class PrivateInfoFormInteraction(Interaction, AbstractInteraction):
    """
    PrivateInfoForm from DocumentsListSupplyInteraction (3rd step of the Scenario)
    """
    required_slots = [
        ClientIsResidentRFSlot,
        ClientServiceRegionSlot,
        ClientPropertyTypeSlot
    ]

    # is_resident = ClientIsResidentRFSlot()

    def start(self, *args, **kwargs):
        print("PrivateInfoFormInteraction.start")

        self.usp = self.ic.DialogPlanner.initialize_user_interaction_proc(self)
        # TODO improve form filling process by abstraction of factory
        # start Slot filling process
        self.ic.DialogPlanner.plan_process_retrieve_slot_value(ClientIsResidentRFSlot,
                                                               callback_fn=self.ClientIsResidentRFSlot_is_filled)

    def ClientIsResidentRFSlot_is_filled(self, *args, **kwargs):

        # TODO improve mechanism of writing slot values?
        # To enable feature to specify target URI in MemoryManager

        self.ic.DialogPlanner.plan_process_retrieve_slot_value(ClientServiceRegionSlot,
                                                               callback_fn=self.ClientServiceRegionSlot_is_filled)



    def ClientServiceRegionSlot_is_filled(self, *args, **kwargs):

        # TODO improve mechanism of writing slot values?
        # To enable feature to specify target URI in MemoryManager
        self.ic.DialogPlanner.plan_process_retrieve_slot_value(ClientPropertyTypeSlot,
                                                               callback_fn=self.ClientPropertyTypeSlot_is_filled)

    def ClientPropertyTypeSlot_is_filled(self, *args, **kwargs):

        # DO complete self process.
        self.ic.DialogPlanner.complete_user_interaction_proc(self)
        pass


class BusinessOfferingInteraction(Interaction, AbstractInteraction):
    """
    4.
    4 BusinessOfferingInteraction
    Предложи открытие счета в рамках Пакетов услуг «Базис+», «Актив+», «Оптима+» или «Зарплатный».
    Согласен ли клиент с условиями пакетов?
        Если клиент не согласен с условиями пакетов, предложить
            Пакет услуг «Минимальный»

    и перейди к шагу 5
    """

    TEXT_BIG_OFFER = """
        BIG_OFFER_TEXT_TEMPLATE.         
        Предложи открытие счета в рамках Пакетов услуг «Базис+», «Актив+», «Оптима+» или «Зарплатный».
        Сообщи: «Пакеты услуг – набор банковских услуг, предоставляемых в течение месяца
         в пределах установленного лимита за определенную плату.
        В состав пакета услуг включены наиболее востребованные услуги
         расчетно-кассового обслуживания, предоставляемые в определенном объеме
         по единой фиксированной цене. При этом стоимость
         пакета услуг ниже стоимости аналогичного
         объема услуг при обслуживании по
         стандартным тарифам Банка. 
        В рамках пакета услуг обязательно 
        подклчается система «Сбербанк Бизнес Онлайн». 
        Также, в рамках 
        Пакетов услуг «Базис+», «Актив+» и «Оптима+» предусмотрена 
        возможность авансовой оплаты за 3 и 6 месяцев, 
        что позволяет сэкономить деньги, а также не беспокоиться 
        о наличии денежных средств на расчетном 
        счете на 01 число каждого месяца для списания
         комиссии за ежемесячное продление Пакета услуг».
        Информация по Пакетам услуг представлена:
        - в БЗ в документе«Пакеты услуг для юр.лиц»
        -на сайтев разделе Расчетно-кассовое обслуживание → Пакеты услуг.
    """

    MINI_OFFER_TEXT = """
    предлагаю вам Пакет услуг «Минимальный» и сообщаю преимущества пакета
    """
    #
    # @classmethod
    # def initialize(cls, ic, name=None, *args, **kwargs):
    #     # TODO remove duplication of initialization
    #     if not name:
    #         # default name is a name of class
    #         name = cls.__name__
    #
    #     intrctn, _ = cls.objects.get_or_create(name=name)
    #     intrctn.ic = ic
    #     super(AbstractInteraction, intrctn).__init__(*args, **kwargs)

        # return intrctn

    def start(self, *args, **kwargs):
        super(self.__class__, self).start(*args, **kwargs)
        # 1. retrieve CurrencySlot
        # self.ic.DialogPlanner.plan_process_retrieve_slot_value(DesiredCurrencySlot).on_slot_filled(
        #     self.on_desired_currency_ready)
        self.ic.DialogPlanner.sendText(self.TEXT_BIG_OFFER)
        self.ic.DialogPlanner.plan_process_retrieve_slot_value(ClientAgreeWithServicePackConditionsSlot,
                                                               callback_fn=self.on_user_decision_on_big_offer_ready)
        print("Ready to go: BusinessOfferingInteraction.start")

    def on_user_decision_on_big_offer_ready(self, *args, **kwargs):
        """
        Клиент согласен с условиями Пакетов?

            Если ДА, перейди к шагу 5

            Если НЕТ, предложи Пакет услуг «Минимальный» и сообщи преимущества Пакета и перейди к шагу 5
        :param args:
        :param kwargs:
        :return:
        """

        big_offer_decision = kwargs['user_slot_process'].result.value
        big_offer_decision = self.ic.MemoryManager.put_slot_value(ClientAgreeWithServicePackConditionsSlot.name,
                                                                     big_offer_decision)
        print(big_offer_decision)
        print("BusinessOfferingInteraction.on_user_decision_on_big_offer_ready method")

        ######################### Completion Busines Rule Block ##########################################
        if ClientAgreeWithServicePackConditionsSlot.ANSWER_YES in big_offer_decision:
            print("ClientAgreeWithServicePackConditionsSlot.ANSWER_YES in big_offer_decision")

            #     then complete self
            self.ic.DialogPlanner.complete_user_interaction_proc(self)

        elif ClientAgreeWithServicePackConditionsSlot.ANSWER_NO in big_offer_decision:
            self.ic.DialogPlanner.sendText(self.MINI_OFFER_TEXT)
            self.ic.DialogPlanner.complete_user_interaction_proc(self, self.EXIT_GATE_OK)

        else:
            import ipdb; ipdb.set_trace()
            raise Exception("BusinessOfferingInteraction.on_user_decision_on_big_offer_ready: unhandled case of user answer")