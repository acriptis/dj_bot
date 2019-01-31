# Startegies: "Greed", "ResumeOnIdle", "Passive",
REQUESTIONING_STRATEGY_DEFAULT = "ResumeOnIdle"

class BaseSlotField():
    """
    Base class for SlotFields
    """

    # "Greed", "ResumeOnIdle", "Passive",
    # requestioning_strategy = "Passive"
    requestioning_strategy = REQUESTIONING_STRATEGY_DEFAULT

    def asker_fn(self):
        return self.questioner

    def get_name(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return self.__class__.__name__


class DictionaryBasedSlotField(BaseSlotField):
    """

        Dictionary based slot uses CANONIC_NAMES list as domain of distinct value classes.

        Each Canonic Name (name of the SlotValueClass) should be supported with Synsets (all possible lexical
        representations of the values in the UserMessage for matching the ValueClass).

        TODO we may need to introduce additional layer of abstraction with normalized synonyms (words in normal form)
        So the alogithm during pattern matching phase will match normal form in Specification with SurfaceForm of Word
        (in particular tense, modality, number etc). Currently we allow only strict match


        Slot with target_uri specification
    """
    def __init__(self, name, domain_of_values_synsets=None, receptor_spec=None, target_uri=None,
                 silent_value=None, confirm_silent_value=False, questioner=None,
                 slot_process_specification_class=None,
                 requestioning_strategy=REQUESTIONING_STRATEGY_DEFAULT):
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
        :param prehistory_extractor_spec: class which may be called before explicit question is asked
            (for filling slot value from dialog prehistory, when user initiates slot filling without questioning,
            this method may implement different algorithm in comparison to ActiveQuestioningProcess Receptor)
        :param requestioning_strategy: may be Greed, Passive, ResumeOnIdle
        :return: UsableSlot

        # TODO WARNING if you patch this class with complex prehistory receptors (which depends on other methods)
        you need to import other methods as weel as method prehistory_recept, recept, can_recept.

        """

        self.name = name
        self.target_uri = target_uri or name
        self.silent_value = silent_value
        self.confirm_silent_value = confirm_silent_value
        self.questioner = questioner

        self.domain_of_values_synsets = domain_of_values_synsets

        # receptor spec must provide methods recept(text, *, **) and can_recept(text, *, **)
        self.receptor_spec = receptor_spec

        self.requestioning_strategy = requestioning_strategy

        # # TODO in future:
        from interactions.models import UserSlotProcess
        if slot_process_specification_class != UserSlotProcess:
            raise Exception("Not implemented functionality (UserSlotProcess as slot_process_specification_class is supported only now!)")

        self.flat_norm = ReceptorFactory.synsets_to_flat_norm_index(self.domain_of_values_synsets)

    def can_recept(self, text, *args, **kwargs):
        return self.receptor_spec.can_recept(self, text, *args, **kwargs)

    def recept(self, text, *args, **kwargs):
        return self.receptor_spec.recept(self, text, *args, **kwargs)

    # def prehistory_recept(self, userdialog):
    #     # import ipdb; ipdb.set_trace()
    #     if self.prehistory_extractor_spec:
    #         try:
    #             return self.prehistory_extractor_spec.prehistory_recept(self, userdialog)
    #         except Exception as e:
    #             import ipdb; ipdb.set_trace()
    #             print(e)
    #
    #     else:
    #         return False, None


# Receptors Base Classes:
class DictionarySlotReceptorMixin():
    """
    MixIn Class that helps dictionary-based slots to recept UserMessages (in natural language)
    Currently only case insensitive matching supported!

    Mixin Requires `synset` attribute to be specified in instance
    """
    # children must specify domain of distinctive slot values classes
    CANONIC_DOMAIN = []
    #
    # # children must define flat norm (Dictionary that provides <surface token> to <canonic form> index
    # flat_norm = {}

    # # TODO add support of MultiCase, Stemming support etc
    # # def __init__(self, canonic_domain):

    def _make_flat_norm(self):
        # construct flat norm
        # index object for translating synonyms into normalized categories:

        self.flat_norm = {}
        for canonic_name, synset in self.synsets.items():
            for each_syn in synset:
                self.flat_norm[each_syn] = canonic_name

    def __init__(self):
        self._make_flat_norm()

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
            if each_cur.lower() in text.lower():
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
            if each_cur.lower() in text.lower():
                results.append(self.flat_norm[each_cur])

        if results:
            # we have something in results
            print("DictionarySlotReceptorMixin.recept: %s grasped results: %s" % (self, results))
            # TODO make productions signals?
        return results

    def prehistory_recept(self, userdialog):
        """
        Method launched after interaction triggering to consume User's directive about time without explicit question

        In this case we may use the same methods of extraction, although in general case
        Prehistory Analysis differs from ExplicitQuestioningAnswer Analysis

        Returns only the most recent match!

        :return: tuple (is_recepted, results)
        """
        # get text of prehistory
        # grasp datetimes mentioned before, the most recent datetimes are more confident estimations
        # print("21222222222222222222222222222222222222222222222222222222")
        # import ipdb; ipdb.set_trace()

        usermessages = userdialog.list_user_messages()
        # search for the recent slot setting (from recent messages to oldest):
        for each_msg in reversed(usermessages):
            can_rec = self.can_recept(each_msg)
            if can_rec:
                results = self.recept(each_msg)
                return can_rec, results

        return False, None


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
            "ДА", "Yes", "Sim", "да", "Да", "Конечно", "Наверное", "Вероятно", "Ок",

        ],
        ANSWER_NO: [
            "НЕТ", "НЕ", "нет", "Нет", "не", "Вряд ли","Едва ли", "Сомневаюсь","Ни за что"

        ],
    }

    def prehistory_recept(self, userdialog):
        """Disable prehistory recepting for default Yes/No, otherwise we may catch irrelevant Yes/No answers"""
        # import ipdb; ipdb.set_trace()

        return False, None

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


class ReceptorInterface():
    """
    Class for description of scheme of Receptors
    """
    def can_recept(self, text, *args, **kwargs):
        """

        Args:
            text:
            *args:
            **kwargs:

        Returns:

        """
        raise Exception("Implement me!")

    def recept(self, text, *args, **kwargs):
        """

        Args:
            text:
            *args:
            **kwargs:

        Returns:

        """
        raise Exception("Implement me!")

    def prehistory_recept(self, userdialog):
        """

        Args:
            userdialog:

        Returns:


        """
        raise Exception("Implement me!")