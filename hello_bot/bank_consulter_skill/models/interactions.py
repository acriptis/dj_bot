# coding=utf-8
from interactions.models import Interaction, AbstractInteraction, SendTextOperation, UserInteraction
from bank_consulter_skill.models.slots import DesiredCurrencySlot, OptionIntentsSlot, NeedListDocsAndTarifsSlot, \
    ClientIsResidentRFSlot, ClientServiceRegionSlot, ClientPropertyTypeSlot, ClientAgreeWithServicePackConditionsSlot, \
    ClientOkToSelfServiceSlot, ClientIsReadyToGiveDocsSlot, ClientWantsNearestOfficeRecomendation


class IntentRetrievalInteraction(Interaction, AbstractInteraction):
    """
    retrieves asks question user for his goal

    and classifies answers into exit gates of different intents

    # TODO
    exit gates or productions signals:
    """
    name = "IntentRetrievalInteraction"

    class Meta:
        proxy = True

    def start(self, *args, **kwargs):
        super(self.__class__, self).start(*args, **kwargs)
        # 1. retrieve OptionIntentsSlot
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=OptionIntentsSlot.name,
                                                                 target_uri=OptionIntentsSlot.name,
                                                                 callback=self.on_intents_ready)

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
        intents_opts = self.ic.MemoryManager.get_slot_value(OptionIntentsSlot.name)

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
                # self.ic.DialogPlanner.enqueue_interaction_by_name("BusinessOfferingInteraction", priority=1)
                self.ic.DialogPlanner.enqueue_interaction_by_name("OnlineReservingFinalizationInteraction", priority=1)
                # TODO generally it better to check if this interaction is not completed yet:
                self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)

        if check_rule_1_1_INTENTER(intents_opts):
            action_rule_1_1_INTENTER()
        else:
            # Exception Scenario
            print("Exception Scenario?")
            import ipdb; ipdb.set_trace()
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

    # name = "DesiredCurrencyInteraction"
    TEXT_2_1 = "Текст 2.1 про то как быть с нерублевыми валютами"

    EXIT_GATE_EXCEPTION = "Oops, Exception"

    class Meta:
        proxy = True

    def start(self, *args, **kwargs):
        print("DesiredCurrencyInteraction.start(")
        super(self.__class__, self).start(*args, **kwargs)
        # 1. retrieve CurrencySlot
        # self.ic.DialogPlanner.plan_process_retrieve_slot_value_by_slot_name(DesiredCurrencySlot.name, callback_fn=self.on_desired_currency_ready)
        # self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(DesiredCurrencySlot.name, callback=self.on_desired_currency_ready)
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=DesiredCurrencySlot.name,
                                                                 target_uri=DesiredCurrencySlot.name,
                                                                 callback=self.on_desired_currency_ready)
    def on_desired_currency_ready(self, *args, **kwargs):
        """
        event handler which
        triggers rule checks
        and precompletion behaviour
        before completing the state of the interaction
        """
        print("DesiredCurrencyInteraction.on_desired_currency_ready(")
        # desired_currency_values = kwargs['user_slot_process'].result.value
        # desired_currency_values = self.ic.MemoryManager.put_slot_value(DesiredCurrencySlot.name,
        #                                                                desired_currency_values)
        desired_currency_values = self.ic.MemoryManager.get_slot_value(DesiredCurrencySlot.name)

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
            return False

        ###################################################
        assert isinstance(desired_currency_values, list), "Unexpected datatype for desired_currency_values: %s, %s" % (desired_currency_values, type(desired_currency_values))

        # special Case for multiple currencies
        nonrub_currencies = list(filter(check_rule_2_1_NONRUB, desired_currency_values))
        if nonrub_currencies:
            # action_rule_2_1_NONRUB
            self.ic.DialogPlanner.sendText(self.TEXT_2_1)
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
    # name = "DocumentsListSupplyInteraction"
    # message to user after the PrivateInfoForm is filled
    # TODO: Uncomment on release:
    # TEXT_3_docs_list_info = """
    #
    #    Действующие спец. предложения:
    #
    #    -спец. предложение для ЮЛ - Клиентов сторонних банков,
    #    у которых отозваны лицензии на
    #    осуществление банковской деятельности
    #    (см.п.9.5 документа Расчетно-кассовое обслуживание);
    #
    #    -спец. предложение для открытия расчетного счета
    #    корпоративным Клиентам (см. документ Расчетно-кассовое обслуживание).
    #    """
    TEXT_3_docs_list_info = "TEXT_3_docs_list_info. Действующие спец. предложения"

    EXIT_GATE_3_1 = "ExitGate3.1"
    # ExitGate(EXIT_GATE_3_1)
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
        self.uip = self.ic.DialogPlanner.initialize_user_interaction_proc(self)
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=NeedListDocsAndTarifsSlot.name,
                                                   target_uri=NeedListDocsAndTarifsSlot.name,
                                                   callback=self.on_response_3_Q1_ready)

    def on_response_3_Q1_ready(self, *args, **kwargs):
        """
        See step 3.Q1 at
        https://www.draw.io/?state=%7B%22ids%22:%5B%221kbtHH-S2G1QbnZM_tuo6KR4RxcMrbu1h%22%5D,%22action%22:%22open%22,%22userId%22:%22110709776902094243429%22%7D#G1kbtHH-S2G1QbnZM_tuo6KR4RxcMrbu1h
        :param args:
        :param kwargs:
        :return:
        """
        needs_tarifs_and_docs = self.ic.MemoryManager.get_slot_value(NeedListDocsAndTarifsSlot.name)
        print(needs_tarifs_and_docs)
        print("on_response_3_Q1_ready method")
        if NeedListDocsAndTarifsSlot.ANSWER_YES in needs_tarifs_and_docs:
            # following interaction encapsulates:
            #     plan Form Filling process,
            #       on completed Send Text
            #     then complete self
            self.ic.DialogPlanner.enqueue_interaction_by_name("PrivateInfoFormInteraction",
                                                              callback_fn=self.on_private_info_form_completed)

        elif NeedListDocsAndTarifsSlot.ANSWER_NO in needs_tarifs_and_docs:

            # assering existence of variable's value:
            print('assering existence of DesiredCurrencySlot value:')

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
    name = "PrivateInfoFormInteraction"
    # is_resident = ClientIsResidentRFSlot()

    def start(self, *args, **kwargs):
        print("PrivateInfoFormInteraction.start")

        self.usp = self.ic.DialogPlanner.initialize_user_interaction_proc(self)
        # TODO improve form filling process by abstraction of factory
        # start Slot filling process
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=ClientIsResidentRFSlot.name,
                                                                 target_uri=ClientIsResidentRFSlot.name,
                                                                 callback=self.client_IsResidentRFSlot_is_filled)

    def client_IsResidentRFSlot_is_filled(self, *args, **kwargs):
        # unused value in dialog management:
        # clientisresidentrfslot_value = self.ic.MemoryManager.get_slot_value(ClientIsResidentRFSlot.name)
        print("ClientIsResidentRFSlot_is_filled")
        # then plan next step
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=ClientServiceRegionSlot.name,
                                                                 target_uri=ClientServiceRegionSlot.name,
                                                                 callback=self.client_ServiceRegionSlot_is_filled)

    def client_ServiceRegionSlot_is_filled(self, *args, **kwargs):
        # unused value in dialog management:
        # clientserviceregionslot_value = self.ic.MemoryManager.get_slot_value(ClientServiceRegionSlot.name)
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=ClientPropertyTypeSlot.name,
                                                                 callback=self.client_PropertyTypeSlot_is_filled)

    def client_PropertyTypeSlot_is_filled(self, *args, **kwargs):
        # unused value in dialog management:
        # clientpropertytypeslot_value = self.ic.MemoryManager.get_slot_value(ClientPropertyTypeSlot.name)
        # # post-filled-actions for explicit memory writing:
        # clientpropertytypeslot_value = kwargs['user_slot_process'].result.value
        # clientpropertytypeslot_value = self.ic.MemoryManager.put_slot_value(ClientPropertyTypeSlot.name,
        #                                                                     clientpropertytypeslot_value)

        # finalize form:
        self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)


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
    name = "BusinessOfferingInteraction"
    TEXT_BIG_OFFER = "BIG_OFFER_TEXT_TEMPLATE."
    # TEXT_BIG_OFFER = """
    #     BIG_OFFER_TEXT_TEMPLATE.
    #     Предложи открытие счета в рамках Пакетов услуг «Базис+», «Актив+», «Оптима+» или «Зарплатный».
    #     Сообщи: «Пакеты услуг – набор банковских услуг, предоставляемых в течение месяца
    #      в пределах установленного лимита за определенную плату.
    #     В состав пакета услуг включены наиболее востребованные услуги
    #      расчетно-кассового обслуживания, предоставляемые в определенном объеме
    #      по единой фиксированной цене. При этом стоимость
    #      пакета услуг ниже стоимости аналогичного
    #      объема услуг при обслуживании по
    #      стандартным тарифам Банка.
    #     В рамках пакета услуг обязательно
    #     подклчается система «Сбербанк Бизнес Онлайн».
    #     Также, в рамках
    #     Пакетов услуг «Базис+», «Актив+» и «Оптима+» предусмотрена
    #     возможность авансовой оплаты за 3 и 6 месяцев,
    #     что позволяет сэкономить деньги, а также не беспокоиться
    #     о наличии денежных средств на расчетном
    #     счете на 01 число каждого месяца для списания
    #      комиссии за ежемесячное продление Пакета услуг».
    #     Информация по Пакетам услуг представлена:
    #     - в БЗ в документе«Пакеты услуг для юр.лиц»
    #     -на сайтев разделе Расчетно-кассовое обслуживание → Пакеты услуг.
    # """

    MINI_OFFER_TEXT = """
    предлагаю вам Пакет услуг «Минимальный» и сообщаю преимущества пакета
    """

    def start(self, *args, **kwargs):
        super(self.__class__, self).start(*args, **kwargs)

        self.ic.DialogPlanner.sendText(self.TEXT_BIG_OFFER)
        # self.ic.DialogPlanner.plan_process_retrieve_slot_value_by_slot_name(ClientAgreeWithServicePackConditionsSlot.name,
        #                                                                     callback_fn=self.on_user_decision_on_big_offer_ready)
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=ClientAgreeWithServicePackConditionsSlot.name,
                                                                 callback=self.on_user_decision_on_big_offer_ready)

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
        big_offer_decision = self.ic.MemoryManager.get_slot_value(ClientAgreeWithServicePackConditionsSlot.name)
        print(big_offer_decision)
        print("BusinessOfferingInteraction.on_user_decision_on_big_offer_ready method")

        ######################### Completion Busines Rule Block ##########################################
        if ClientAgreeWithServicePackConditionsSlot.ANSWER_YES in big_offer_decision:
            print("ClientAgreeWithServicePackConditionsSlot.ANSWER_YES in big_offer_decision")

            #     then complete self
            self.ic.DialogPlanner.complete_user_interaction_proc(self, self.EXIT_GATE_OK)

        elif ClientAgreeWithServicePackConditionsSlot.ANSWER_NO in big_offer_decision:
            print("ClientAgreeWithServicePackConditionsSlot.ANSWER_NO in big_offer_decision")
            self.ic.DialogPlanner.sendText(self.MINI_OFFER_TEXT)
            self.ic.DialogPlanner.complete_user_interaction_proc(self, self.EXIT_GATE_OK)

        else:
            import ipdb; ipdb.set_trace()
            raise Exception("BusinessOfferingInteraction.on_user_decision_on_big_offer_ready: unhandled case of user answer")

class ConsideringSelfServiceInteraction(Interaction, AbstractInteraction):

    """
        Удобно ли Клиенту самостоятельно ознакомиться с документами и тарифами на сайте Банка?

        Если ДА,

        Если НЕТ,
        сообщи об условиях открытия счета, сроках открытия, требуемых документах, согласно документу Расчетно-кассовое обслуживание, а также тарифах, согласно информации на сайте.

        проконсультируй клиента о преимуществах Сбербанк Бизнес Онлайн (назови Клиенту не менее одного), согласно документу Удаленное обслуживание (Карточка продукта)

        Перейди к шагу 6

        asks the currency of the account to be opened

        Does logic of Handling NONRUB case

        uses
            ClientOkToSelfServiceSlot.name


        exit gates:
        1. ExitGate_Ok (default)

        """

    name = "ConsideringSelfServiceInteraction"

    # TEXT_5_YES = """
    #         сообщи путь размещения перечня документов на сайте
    #     Банка в зависимости от того, оформляет клиент
    #     «Договор банковского счета» или «Договор-конструктор»:
    #     - Малому бизнесу/Корпоративным клиентам – Банковское обслуживание
    #     – Расчетно-кассовое обслуживание – Открытие и ведение счетов /
    #     Договор банковского счета /
    #     Приложение №1 «Перечень документов, необходимых для открытия и ведения Счета»
    #     - Малому бизнесу/Корпоративным клиентам – Банковское обслуживание –
    #      Расчетно-кассовое обслуживание – Открытие и ведение счетов
    #      / Договор-конструктор / Тарифы Договоры Операционное время /
    #     Перечень документов, необходимых для заключения
    #     Договора-Конструктора с 01.01.2015
    #     сообщи путь размещения тарифов на сайте www.sberbank.ru:
    #     раздел Малому бизнесу → Расчетно-кассовое обслуживание →
    #     Полный перечень всех тарифов на услуги РКО → выбрать регион обслуживания.
    #     раздел Корпоративным клиентам → Расчетно-кассовое обслуживание →
    #      Тарифы и операционное время → выбрать регион обслуживания.
    #     проконсультируй клиента о преимуществах Сбербанк
    #     Бизнес Онлайн (назови Клиенту не менее одного),
    #     согласно документу Удаленное обслуживание (Карточка продукта)
    # """
    TEXT_5_YES = "TEXT_5_YES"
    TEXT_5_NO = "TEXT_5_NO"
    # EXIT_GATE_EXCEPTION = "Oops, Exception"

    class Meta:
        proxy = True

    def start(self, *args, **kwargs):
        print("ConsideringSelfServiceInteraction.start(")
        super(self.__class__, self).start(*args, **kwargs)
        # 1. retrieve CurrencySlot
        # check if it is not retrieved yet?

        # self.ic.DialogPlanner.plan_process_retrieve_slot_value_by_slot_name(ClientOkToSelfServiceSlot.name,
        #                                                                     callback_fn=self.when_client_responded_about_self_serving)
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=ClientOkToSelfServiceSlot.name,
                                                                 callback=self.when_client_responded_about_self_serving)

    def when_client_responded_about_self_serving(self, *args, **kwargs):
        """
        event handler which
        triggers rule checks
        and precompletion behaviour
        before completing the state of the interaction
        """
        print("ConsideringSelfServiceInteraction.when_client_responded_about_self_serving(")
        self_serving_answer = self.ic.MemoryManager.get_slot_value(ClientOkToSelfServiceSlot.name)
        ######################### Busines Rule BR5 Block ##########################################

        ######################### Completion Busines Rule Block ##########################################
        if ClientOkToSelfServiceSlot.ANSWER_YES in self_serving_answer:
            print("ClientOkToSelfServiceSlot.ANSWER_YES in self_serving_answer")
            self.ic.DialogPlanner.sendText(self.TEXT_5_YES)

        elif ClientOkToSelfServiceSlot.ANSWER_NO in self_serving_answer:
            print("ClientOkToSelfServiceSlot.ANSWER_NO in self_serving_answer")
            self.ic.DialogPlanner.sendText(self.TEXT_5_NO)

        else:
            import ipdb;
            ipdb.set_trace()
            raise Exception(
                "ClientOkToSelfServiceSlot.when_client_responded_about_self_serving: unhandled case of user answer")

        ######################### END Busines Rule BR5 Block ##########################################

        self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)
# ###################################################################################################


# ###################################################################################################

class OnlineReservingFinalizationInteraction(Interaction, AbstractInteraction):
    """
    6 Шаг скрипта
    """
    TEXT_6_RUB_DOCS_LIST = "TEXT_6_RUB_DOCS_LIST"
    TEXT_6_NONRUB_DOCS_INFO = "TEXT_6_NONRUB_DOCS_INFO"
    TEXT_6_RUB_READY_REDIRECT = "TEXT_6_RUB_READY_REDIRECT"
    TEXT_6_RUB_NOT_READY_ASK_RETRY_LATER = "TEXT_6_RUB_NOT_READY_ASK_RETRY_LATER"

    EXIT_GATE_6_NONRUB_RESERVATION_OFFLINE = "EXIT_GATE_6_NONRUB_RESERVATION_OFFLINE"
    # ExitGate(EXIT_GATE_3_1)
    EXIT_GATE_6_RUB_UNREADY = "EXIT_GATE_6_RUB_UNREADY"
    EXIT_GATE_6_RUB_READY = "EXIT_GATE_6_RUB_READY"

    # Custom exit gates must be declared explicitly
    EXIT_GATES_NAMES_LIST = [
        EXIT_GATE_6_NONRUB_RESERVATION_OFFLINE,
        EXIT_GATE_6_RUB_UNREADY,
        EXIT_GATE_6_RUB_READY
    ]

    class Meta:
        proxy = True

    def start(self, *args, **kwargs):
        print("Ready to go: OnlineReservingFinalizationInteraction.start")
        super(self.__class__, self).start(*args, **kwargs)
        self.uip = self.ic.DialogPlanner.initialize_user_interaction_proc(self)

        # TODO: design practice of slot retrieval (when self doesnt know wether slot is memorized or not elicited yet)
        # the slot retrieval for slots which following line should be async aware if slot is not exist
        # Approach 1: (dirty and easy) use request-callback pattern, by requesting slot value and transfering it
        # to callback
        # Approach 2: (clean and async) use async pattern: https://habr.com/post/266743/

        # self.ic.remind_or_retrieve_slot(slot_spec=DesiredCurrencySlot, target_uri=DesiredCurrencySlot.name, callback=self.after_desired_currency_slot_evaluated)
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(
            slot_spec_name=DesiredCurrencySlot.name,
            target_uri=DesiredCurrencySlot.name,
            callback=self.after_desired_currency_slot_evaluated)

    def after_desired_currency_slot_evaluated(self, *args, **kwargs):
        # TODO make up more general solution ?
        # assering existence of variable's value:
        print('assering existence of DesiredCurrencySlot value in memory')
        desired_currency_slot_value = self.ic.MemoryManager.get_slot_value(DesiredCurrencySlot.name)

        if DesiredCurrencySlot.RUB in desired_currency_slot_value:
            self.ic.DialogPlanner.sendText(self.TEXT_6_RUB_DOCS_LIST)
            # self.ic.DialogPlanner.plan_process_retrieve_slot_value_by_slot_name(ClientIsReadyToGiveDocsSlot.name,
            #                                                                     callback_fn=self.on_client_responded_if_docs_ready)
            self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(ClientIsReadyToGiveDocsSlot.name,
                                                                     callback=self.on_client_responded_if_docs_ready)
        # Возможны случаи когда клиент упомянул две и более валюты
        # рублевую и нерублевую, в этом случае поведение не определено однозначно

        # TODO:
        # really it is a hack: we must check NONRUB
        if DesiredCurrencySlot.USD in desired_currency_slot_value:
            self.ic.DialogPlanner.sendText(self.TEXT_6_NONRUB_DOCS_INFO)
            self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_6_NONRUB_RESERVATION_OFFLINE)

    def on_client_responded_if_docs_ready(self, *args, **kwargs):
        """
        Switch 6.2 at step 6
        :param args:
        :param kwargs:
        :return:
        """
        ready_to_give_docs = self.ic.MemoryManager.get_slot_value(ClientIsReadyToGiveDocsSlot.name)
        print(ready_to_give_docs)
        print("on_client_responded_if_docs_ready")
        if ClientIsReadyToGiveDocsSlot.ANSWER_YES in ready_to_give_docs:
            self.ic.DialogPlanner.sendText(self.TEXT_6_RUB_READY_REDIRECT)

            self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_6_RUB_READY)
            # self.ic.DialogPlanner.enqueue_interaction_by_name("PrivateInfoFormInteraction",
            #                                                   callback_fn=self.on_private_info_form_completed)

        elif ClientIsReadyToGiveDocsSlot.ANSWER_NO in ready_to_give_docs:
            self.ic.DialogPlanner.sendText(self.TEXT_6_RUB_NOT_READY_ASK_RETRY_LATER)
            self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_6_RUB_UNREADY)


class OfficeRecommendationInteraction(Interaction, AbstractInteraction):
    """
        Step 7
        Сообщи Клиенту: «Подобрать для Вас ближайший
        к Вам офис Банка, который работает с юридическими лицами?»
        При необходимости предоставь клиенту
        адрес, телефон и режим работы соответствующего офиса.*

        *в офис по адресу г. Москва,
        ул. Вавилова, 19 не направлять!
        При поступлении вопросов
        проконсультируй Клиента в соответствии с действующими процедурами.
        Перейди к шагу 8

    """

    TEXT_ADDRESS_RECOMENDATION = "Советую вам не идти по адресу ул. Вавилова, 19"

    class Meta:
        proxy = True

    def start(self, *args, **kwargs):
        print("Ready to go: OfficeRecommendationInteraction.start")
        super(self.__class__, self).start(*args, **kwargs)
        self.uip = self.ic.DialogPlanner.initialize_user_interaction_proc(self)
        # self.ic.DialogPlanner.plan_process_retrieve_slot_value_by_slot_name(ClientWantsNearestOfficeRecomendation.name,
        #                                                                     callback_fn=self.on_answer_about_nearest_office_recomendation)
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(ClientWantsNearestOfficeRecomendation.name,
                                                                 callback=self.on_answer_about_nearest_office_recomendation)

    def on_answer_about_nearest_office_recomendation(self, *args, **kwargs):
        """
        event handler which
        triggers rule checks
        and precompletion behaviour
        before completing the state of the interaction
        """
        print("OfficeRecommendationInteraction.on_answer_about_nearest_office_recomendation(")
        answer = self.ic.MemoryManager.get_slot_value(ClientWantsNearestOfficeRecomendation.name)
        if ClientWantsNearestOfficeRecomendation.ANSWER_YES in answer:
            # really we need to do here interaction with
            # 1. locatioon retrieval
            # 2. search of knwoledge base of addresses of the offices
            # 3. find the nearest
            # 4. verbose results
            self.ic.DialogPlanner.sendText(self.TEXT_ADDRESS_RECOMENDATION)

            self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)

        elif ClientWantsNearestOfficeRecomendation.ANSWER_NO in answer:

            self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)


class DialogTerminationInteraction(Interaction, AbstractInteraction):
    class Meta:
        proxy = True

    def start(self, *args, **kwargs):
        print("Ready to go: DialogTerminationInteraction.start")
        super(self.__class__, self).start(*args, **kwargs)
        self.uip = self.ic.DialogPlanner.initialize_user_interaction_proc(self)
        # hack to announce that scenaric dialog is finished
        self.ic.MemoryManager.put_slot_value("bank_scenario.terminated", True)
        self.ic.DialogPlanner.sendText("На этом завершим разговор.")


from components.matchers.matchers import PhrasesMatcher
class OperatorSwitchInteraction(Interaction, AbstractInteraction):
    class Meta:
        proxy = True

    def post_init_hook(self):
        """
        The post-initialize hook  for attaching global receptors.

        Here we connect the interaction's Global Receptors with InformationController
        :return:
        """
        # this Interaction may be activated by Receptor (actually it is binary intent classifier here)
        self.global_trigger_receptor = PhrasesMatcher(phrases=["ОПЕРАТОР", "Переключите меня на оператора"],
                                                      daemon_if_matched=self.start)
        self.ic.user_message_signal.connect(self.global_trigger_receptor)


    def start(self, *args, **kwargs):
        print("Ready to go: OperatorSwitchInteraction.start")
        super(self.__class__, self).start(*args, **kwargs)
        self.uip = self.ic.DialogPlanner.initialize_user_interaction_proc(self)
        # hack to announce that scenaric dialog is finished
        self.ic.MemoryManager.put_slot_value("bank_scenario.terminated", True)
        self.ic.DialogPlanner.sendText("Переключаю Вас на оператора...")
