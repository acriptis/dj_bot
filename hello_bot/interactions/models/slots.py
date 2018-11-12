from django.db import models

class BaseSlotField():
    """
    Base class for SlotFields
    """
    pass

class DictionarySlotReceptorMixin():
    """
    Class is MixIn that helps dictionary-based slots handle answers (in natural language)
    """
    # children must specify domain of distinctive slot values classes

    CANONIC_DOMAIN = []
    # children must define flat norm
    flat_norm = {}

    def can_recept(self, text, *args, **kwargs):
        """
        Method that checks if UserMessage can be recepted by Receptor

        :param text:
        :param args:
        :param kwargs:
        :return: True/False
        # TODO partial reception of the message!
        """
        for each_cur in self.flat_norm.keys():
            if each_cur in text:
                return True

        else:
            return False

    def recept(self, text, *args, **kwargs):
        """
        Method that actually recepts message and extracts Slot's Value from it
        :param text:
        :param args:
        :param kwargs:
        :return:
        """
        results = []
        for each_cur in self.flat_norm.keys():
            if each_cur in text:
                results.append(self.flat_norm[each_cur])

        if results:
            # we have something in results
            print("We have results!")
            # TODO make productions signals?
        return results


class YesNoSlotReceptorMixin(DictionarySlotReceptorMixin):
    """
    Class is MixIn that helps to handle Yes-No answers (in natural language)
    """
    ######################################################
    # Slot's Values Domain Specification
    ANSWER_YES = "Yes"
    ANSWER_NO = "No"

    # TODO  if user wants nothing we may should use greed strategy of slot requestioning

    CANONIC_DOMAIN = [ANSWER_YES, ANSWER_NO]

    # synonyms set:
    # capitals for case insensitive pattern search
    synsets = {
        ANSWER_YES: [
            "ДА", "Yes", "Sim"
        ],
        ANSWER_NO: [
            "НЕТ", "НЕ",
        ],
    }

    # index object for translating synonyms into normalized categories:
    flat_norm = {}
    for canonic_name, synset in synsets.items():
        for each_syn in synset:
            flat_norm[each_syn] = canonic_name

################################################################################################

### Drafts:
class SlotField(models.Model):

    name = models.CharField(max_length=200)

    validator = models.CharField(max_length=200)

    normalizer = models.CharField(max_length=200)

    receptor = models.CharField(max_length=200)

    required = models.BooleanField()

    #
    #
    # def __init__(self,  target_uri, slot_type, asker_fn, receptor_fn, validator_fn, normalizer_fn,
    #              required, elicitable, *args, **kwargs):
    #     """
    #
    #     :param target_uri:
    #     :param slot_type: type of Slot' Value
    #     :param receptor_fn:
    #     :param asker_fn: the function to ask question to user about value of the slot
    #         and connecting answer receptor to signal system
    #     :param validator_fn:
    #     :param question:
    #     :param if_requested:
    #     :param if_added:
    #     :param if_removed:
    #     :param if_updated:
    #     :param required:
    #     :param elicitable:
    #     :param args:
    #     :param kwargs:
    #     """
    #     pass

# class