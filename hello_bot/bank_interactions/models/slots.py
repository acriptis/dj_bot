from components.slots.city_slot import CitySlot
from components.slots.slots import BaseSlotField, DictionarySlotReceptorMixin, YesNoSlotReceptorMixin


class OptionIntentsSlot(BaseSlotField, DictionarySlotReceptorMixin):
    """
    1 Шаг Сценрия запрашивает у пользователя инфомрацию о намерении, ожидая получить
     выбор опций:
      COMMON_INFO и/или SECRET_INFO
    """
    name = "OptionIntentsSlot"

    questioner = "Я могу рассказать Общие Сведения об открытии счетов для юридических лиц, " \
                 "а также Секретную Информацию для посвященных об открытии счетов. \n" \
                 "Что вас интересует?"

    ######################################################
    # Slot's Values Domain Specification
    COMMON_INFO = "CommonInfoOption"

    SECRET_INFO = "SecretInfoOption"

    # TODO  if user wants nothing we may should use greed strategy of slot requestioning

    CANONIC_DOMAIN = [COMMON_INFO, SECRET_INFO]

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

    ################################################################################################


class DesiredCurrencySlot(BaseSlotField, DictionarySlotReceptorMixin):
    """
    Slot for requesting desired currency of user.

    TODO make as child class of CurrencySlot
    """
    # TODO fix potential discrepancy between name of class and name of instance
    name = 'DesiredCurrencySlot'

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
    ################################################################################################


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


class ClientServiceRegionSlot(CitySlot):
    name = 'ClientServiceRegionSlot'

    questioner = "В каком регионе обитаете?"


class ClientPropertyTypeSlot(BaseSlotField, DictionarySlotReceptorMixin):
    name = 'ClientPropertyTypeSlot'

    questioner = "Какой у вас тип собственности?"

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


class ClientWantsNearestOfficeRecomendation(BaseSlotField, YesNoSlotReceptorMixin):
        """
        Slot for requesting user step7's question

        """
        name = 'ClientWantsNearestOfficeRecomendation'

        questioner = "Подобрать для Вас ближайший к Вам офис Банка, который работает с юридическими лицами?"

        ######################################################
        # Slot's Values Domain Specification
        # Don't need it because we use YesNo Receptors'
        ################################################################################################
