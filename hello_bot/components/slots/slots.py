from django.db import models

class BaseDjangoSlotField():
    def __init__(self, *, required=True, widget=None, label=None, initial=None,
                 help_text='', error_messages=None, show_hidden_initial=False,
                 validators=(), localize=False, disabled=False, label_suffix=None):
        # required -- Boolean that specifies whether the field is required.
        #             True by default.
        # widget -- A Widget class, or instance of a Widget class, that should
        #           be used for this Field when displaying it. Each Field has a
        #           default Widget that it'll use if you don't specify this. In
        #           most cases, the default widget is TextInput.
        # label -- A verbose name for this field, for use in displaying this
        #          field in a form. By default, Django will use a "pretty"
        #          version of the form field name, if the Field is part of a
        #          Form.
        # initial -- A value to use in this Field's initial display. This value
        #            is *not* used as a fallback if data isn't given.
        # help_text -- An optional string to use as "help text" for this Field.
        # error_messages -- An optional dictionary to override the default
        #                   messages that the field will raise.
        # show_hidden_initial -- Boolean that specifies if it is needed to render a
        #                        hidden widget with initial value after widget.
        # validators -- List of additional validators to use
        # localize -- Boolean that specifies if the field should be localized.
        # disabled -- Boolean that specifies whether the field is disabled, that
        #             is its widget is shown in the form but not editable.
        # label_suffix -- Suffix to be added to the label. Overrides
        #                 form's label_suffix.
        pass

class BaseSlotField():
    """
    Base class for SlotFields
    """

    def asker_fn(self):
        return self.questioner
    #
    # @classmethod
    # def get_name(cls):
    #     return cls.__name__

    def get_name(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return self.__class__.__name__


class DictionaryBasedSlotField(BaseSlotField):
    """
        Dictioanry based slot uses CANONIC_NAMES as domin of values
        each Canonic value may be complemented with synsets (all lexical representations of the
        slot in the UserMessage)
    """
    def __init__(self, name, domain_of_values_synsets=None, receptor_spec=None, target_uri=None,
                 silent_value=None, confirm_silent_value=False, questioner=None,
                 slot_process_specification_class=None, prehistory_extractor_fn=None):
        """
        A factory method for dictionary based slots

        :param name: reference name for registry
        :param target_uri: reference name for URI of slot value in the memory, if None then the same as @name used
        :param silent_value: value that is used if no information was provided by user initiative (or default value)
        :param confirm_silent_value: should slot process request confirmation from user about silent value (if user have not provided value explicitly)
        :param questioner: question string (or questioning function for template based questions)
        :param receptor_spec: UserMessageReceptor specification, mixin class for recepting slot value

        :param domain_of_values_synsets: for dictionary based slots we need to specify domain of values and their synonyms
        :param slot_process_specification_class: SlotProcess specifies ReAskingStrategy, PreHistory analysis
            default is SlotProcess
        :param prehistory_extractor_fn: method which may be called before explicit question is asked
            (for filling slot value by message said by user)
        :return: UsableSlot
        """

        self.name = name
        self.target_uri = target_uri or name
        self.silent_value = silent_value
        self.confirm_silent_value = confirm_silent_value
        self.questioner = questioner

        self.domain_of_values_synsets = domain_of_values_synsets

        # receptor spec must provide methods recept(text, *, **) and can_recept(text, *, **)
        self.receptor_spec = receptor_spec


        # # TODO in future:
        from interactions.models import UserSlotProcess
        if slot_process_specification_class != UserSlotProcess:
            raise Exception("Not implemented functionality (UserSlotProcess as slot_process_specification_class is supported only now!)")

        if prehistory_extractor_fn:
            raise Exception("Not implemented functionality (prehistory_extractor_fn)")

        self.flat_norm = ReceptorFactory.synsets_to_flat_norm_index(self.domain_of_values_synsets)

    def can_recept(self, text, *args, **kwargs):
        # import ipdb; ipdb.set_trace()

        return self.receptor_spec.can_recept(self, text, *args, **kwargs)

    def recept(self, text, *args, **kwargs):
        return self.receptor_spec.recept(self, text, *args, **kwargs)


# Receptors Base Classes:
class DictionarySlotReceptorMixin():
    """
    Class is MixIn that helps dictionary-based slots handle answers (in natural language)
    """
    # children must specify domain of distinctive slot values classes
    CANONIC_DOMAIN = []

    # children must define flat norm (Dictionary that provides <surface token> to <canonic form> index
    flat_norm = {}
    # TODO add support of MultiCase, Stemming support etc
    # def __init__(self, canonic_domain):

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
            print("DictionarySlotReceptorMixin.recept: %s grasped results: %s" % (self, results))
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


class ReceptorFactory():
    """
    Constructs a pair of receptor function (SlotReceptorMixin) + domain of allowed values
    """
    @classmethod
    def make_receptor(cls, receptor_template_class, domain_of_values_synsets):
        """
        Constructs a Receptor Instance which may be mixed into slot declaration
        :param receptor_template_class:
        :param domain_of_values_synsets:
        :return:
        """
        receptor_mixin_instance = receptor_template_class()
        receptor_mixin_instance.CANONIC_DOMAIN = domain_of_values_synsets.keys()
        receptor_mixin_instance.synsets = domain_of_values_synsets
        receptor_mixin_instance.flat_norm = ReceptorFactory.synsets_to_flat_norm_index(domain_of_values_synsets)
        return receptor_mixin_instance

    @classmethod
    def synsets_to_flat_norm_index(cls, domain_of_values_synsets):
        """
        :param domain_of_values_synsets:

        Converts dictionary of domain values like
        domain_of_values_synsets =
        {
            CANONIC_NAME1: [synonym1, synonym2, ...]
            CANONIC_NAME2: [synonym21, synonym22, ...]
        }
        into

        flat_norm =
        {
            synonym1: CANONIC_NAME1
            synonym2: CANONIC_NAME1
            synonym21: CANONIC_NAME2
            synonym22: CANONIC_NAME2
        }

        :return: flat_norm
        """
        flat_norm = {}
        for canonic_name, synset in domain_of_values_synsets.items():
            for each_syn in synset:
                flat_norm[each_syn] = canonic_name

        return flat_norm

#
# loc_receptor = ReceptorFactory.make_dictionary_based_receptor(
#     domain_of_values_synsets=1,
#     receptor_template_class=DictionarySlotReceptorMixin
#     )
# loc_slot = make_slot(
#     name='LocationSlot',
#     # or maybe silent function which retrieves slot value from user profile or remote function?
#     silent_value="Москва",
#     questioner="В каком городе?",
#     receptor_spec=loc_receptor
#
# )
#
# class CityLocationSlot(BaseSlotField):
#     questioner = "В каком городе?"
#
#
#
# class DateSlot():
#     pass
