from interactions.models.slots import BaseSlotField, DictionarySlotReceptorMixin, YesNoSlotReceptorMixin


class OptionIntentsSlot(BaseSlotField, DictionarySlotReceptorMixin):
    """
    1 Шаг Сценрия запрашивает у пользователя инфомрацию о намерении, ожидая получить
     выбор опций:
      COMMON_INFO и/или SECRET_INFO
    """
    name = "intents"

    questioner = "Я могу рассказать Общие Сведения об открытии счетов для юридических лиц, " \
                 "а также Секретную Информацию для посвященных об открытии счетов. \n" \
                 "Что вас интересует?"

    ######################################################
    # Slot's Values Domain Specification
    COMMON_INFO = "CommonInfoOption"

    SECRET_INFO = "SecretInfoOption"

    # if user intents nothing, we use it as Exception scenario in case if nothing optioned
    NOTHING = "Nothing"

    # TODO  if user wants nothing we may should use greed strategy of slot requestioning

    CANONIC_DOMAIN = [COMMON_INFO, SECRET_INFO, NOTHING]

    # synonyms set:
    # capitals for case insensitive pattern search
    synsets= {
        COMMON_INFO: [
            "ОБЩАЯ"
        ],
        SECRET_INFO: [
            "ДОПОЛНИТЕЛЬН", "СЕКРЕТ",
        ],
    }

    # index object for translating synonyms into normalized categories:
    flat_norm = {}
    for canonic_name, synset in synsets.items():
        for each_syn in synset:
            flat_norm[each_syn] = canonic_name
    ################################################################################################

    def asker_fn(self):
        return self.questioner


class DesiredCurrencySlot(BaseSlotField, DictionarySlotReceptorMixin):
    """
    Slot for requesting desired currency of user.

    TODO make as child class of CurrencySlot
    """
    name = 'desired_currency'

    questioner = "В какой валюте?"

    ######################################################
    # Slot's Values Domain Specification
    RUB = "RUB"
    USD = "USD"
    CANONIC_DOMAIN = [RUB, USD]

    # synonyms set:
    synsets= {
        RUB: [
            "РУБЛИ", "руб"
        ],
        USD: [
            "БАКСЫ"
        ]

    }

    # TODO move into abstract?
    # index object for translating synonyms into normalized categories:
    flat_norm = {}
    for canonic_name, synset in synsets.items():
        for each_syn in synset:
            flat_norm[each_syn] = canonic_name
    ################################################################################################

    # TODO move into abstract
    def asker_fn(self):
        return self.questioner

# 3 DocumentsListSupplyInteraction
# NeedListDocsAndTarifsSlot
# if user needs information about documents and tarifs

class NeedListDocsAndTarifsSlot(BaseSlotField, YesNoSlotReceptorMixin):
    """
    Slot for requesting if user needs a list of docs and tarifs

    """
    name = 'NeedListDocsAndTarifsSlot'

    questioner = "Интересуют ли вас перечень документов для открытия счета и " \
                 "тарифы на открытие и обслуживание счета?"

    ######################################################
    # Slot's Values Domain Specification
    # Don't need it because we use YesNo Receptors'
    ################################################################################################




# #################################################################################
# part of PrivateInfoForm:
class ClientIsResidentRFSlot(BaseSlotField, YesNoSlotReceptorMixin):
    name = 'ClientIsResidentRFSlot'

    questioner = "Вы резидент РФ?"

    # TODO move into abstract
    def asker_fn(self):
        return self.questioner

class ClientServiceRegionSlot(BaseSlotField, DictionarySlotReceptorMixin):
    name = 'ClientServiceRegionSlot'

    questioner = "В каком регионе обитаете?"

    ######################################################
    # Slot's Values Domain Specification
    MSK = "Moscow"
    BOBRU = "Bobruisk"
    CANONIC_DOMAIN = [MSK, BOBRU]

    # synonyms set:
    synsets = {
        MSK: [
            "МОСКВА", "МСК"
        ],
        BOBRU: [
            "БОБРУЙСК", "БОБРУИСК"
        ]

    }

    # TODO move into abstract?
    # index object for translating synonyms into normalized categories:
    flat_norm = {}
    for canonic_name, synset in synsets.items():
        for each_syn in synset:
            flat_norm[each_syn] = canonic_name


class ClientPropertyTypeSlot(BaseSlotField, DictionarySlotReceptorMixin):
    name = 'ClientPropertyTypeSlot'

    questioner = "Какой у вас тип собственности"

    ######################################################
    # Slot's Values Domain Specification
    PROP_TYPE_IP = "ИП"
    PROP_TYPE_OOO = "ООО"
    CANONIC_DOMAIN = [PROP_TYPE_IP, PROP_TYPE_OOO]

    # synonyms set:
    synsets = {
        PROP_TYPE_IP: [
            "ИП", "предприниматель"
        ],
        PROP_TYPE_OOO: [
            "ООО",
        ]

    }

    # TODO move into abstract?
    # index object for translating synonyms into normalized categories:
    flat_norm = {}
    for canonic_name, synset in synsets.items():
        for each_syn in synset:
            flat_norm[each_syn] = canonic_name


class ClientAgreeWithServicePackConditionsSlot(BaseSlotField, YesNoSlotReceptorMixin):
    """
    Slot for requesting if user approves Big Offer (see: 4 BusinessOfferingInteraction)

    """
    name = 'ClientAgreeWithServicePackConditionsSlot'

    questioner = "Вы согласны с условиями Пакетов?"

    ######################################################
    # Slot's Values Domain Specification
    # Don't need it because we use YesNo Receptors'
    ################################################################################################


    # TODO move into abstract
    def asker_fn(self):
        return self.questioner

    # def can_recept(self, text, *args, **kwargs):
    #     """
    #     Method that checks if UserMessage can be recepted by Receptor
    #
    #     :param text:
    #     :param args:
    #     :param kwargs:
    #     :return: True/False
    #     # TODO partial reception of the message!
    #     """
    #     import ipdb; ipdb.set_trace()
    #
    #     for each_cur in self.flat_norm.keys():
    #         if each_cur in text:
    #             return True
    #
    #     else:
    #         return False
    #
    # def recept(self, text, *args, **kwargs):
    #     """
    #     Method that actually recepts message and extracts Slot's Value from it
    #     :param text:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #     results = []
    #     for each_cur in self.flat_norm.keys():
    #         if each_cur in text:
    #             results.append(self.flat_norm[each_cur])
    #
    #     if results:
    #         # we have something in results
    #         print("DictionarySlotReceptorMixin.recept: %s grasped results: %s" % (self, results))
    #         # TODO make productions signals?
    #     return results

# END Slots of PrivateInfoForm:
#################################################################################



class ClientOkToSelfServiceSlot(BaseSlotField, YesNoSlotReceptorMixin):
    """
    Slot for requesting if user step5 question

    """
    name = 'ClientOkToSelfServiceSlot'

    questioner = "Удобно ли вам самостоятельно ознакомиться с документами и тарифами на сайте Банка?"

    ######################################################
    # Slot's Values Domain Specification
    # Don't need it because we use YesNo Receptors'
    ################################################################################################


    # TODO move into abstract
    def asker_fn(self):
        return self.questioner


class ClientIsReadyToGiveDocsSlot(BaseSlotField, YesNoSlotReceptorMixin):
        """
        Slot for requesting user step6's question

        """
        name = 'ClientIsReadyToGiveDocsSlot'

        questioner = "Вы готовы предоставить документы?"

        ######################################################
        # Slot's Values Domain Specification
        # Don't need it because we use YesNo Receptors'
        ################################################################################################

        # TODO move into abstract
        def asker_fn(self):
            return self.questioner
