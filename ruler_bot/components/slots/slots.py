# Startegies: "Greed", "ResumeOnIdle", "Passive",
from components.utils.mongoengine_get_or_create_mixin import MongoEngineGetOrCreateMixin

REQUESTIONING_STRATEGY_DEFAULT = "ResumeOnIdle"

from mongoengine import DynamicDocument, StringField, Document, DynamicField, ListField


class BaseSlot(Document, MongoEngineGetOrCreateMixin):
    """
    Base class for SlotFields


    """

    # "Greed", "ResumeOnIdle", "Passive",
    # requestioning_strategy = "Passive"
    requestioning_strategy = REQUESTIONING_STRATEGY_DEFAULT

    # # slot type name
    # type_name = StringField()

    # slot unique name, for referencing in the RuntimeSystem
    name = StringField()

    # currently querstion is the only one question
    questioner = StringField(required=False)

    # value which is taken if no value provided in prehistory
    # (silent value allows to avoid ActiveQuestioning for inferred slots)
    silent_value=DynamicField(required=False)

    meta = {
        "allow_inheritance": True
    }
    # TODO finalize model
    # # value silently assumed when user hadn't initiated setting of the slot value
    # silent_value = DynamicField(required=False)
    # confirm_silent_value = False,
    # slot_process_specification_class = None,
    # requestioning_strategy = REQUESTIONING_STRATEGY_DEFAULT)

    # #############################################################################################
    # ######### VVVV Slot declaration section VVVV #####################################
    def asker_fn(self):
        return self.questioner

    def get_name(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return self.__class__.__name__

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        return self.get_name()

    # #############################################################################################
    # ######### VVVV Slot evaluation implementation section VV ####################################
    def can_recept(self, text, *args, **kwargs):
        """
        Method that checks if UserMessage can be recepted by Receptor

        :param text:
        :param args:
        :param kwargs:
        :return: True/False

        """
        raise Exception("Implement me!")

    def recept(self, text, *args, **kwargs):
        """
        Method that actually recepts message and extracts Slot's Value from it

        Args:
            text: text to be analyzed (str)
            *args:
            **kwargs:

        Returns:

        """
        raise Exception("Implement me!")

    def prehistory_recept(self, userdialog):
        """
        Prehistory recept is not imp[;lemented for TextReceptor because it greedy consumes text
        :return: tuple (is_recepted, results)
        """

        raise Exception("Implement me!")


class FreeTextSlot(BaseSlot):
    """Class for Slots which greedly absorb the text message after the intiation of
    ActiveQuestioningProcess.

    This class rejects prehistory recepting, because it does no validation to distinct right text
    from non relevant text
    """
    meta = {
        "allow_inheritance": True
    }

    def can_recept(self, text, *args, **kwargs):
        """
        Method that checks if UserMessage can be recepted by Receptor

        :param text:
        :param args:
        :param kwargs:
        :return: True/False

        """
        # such slot always can recept (when message is not empty) because it consumes the message
        if text:
            return True
        else:
            return False

    def recept(self, text, *args, **kwargs):
        """
        Method that actually recepts message and extracts Slot's Value from it

        Args:
            text: text to be analyzed (str)
            *args:
            **kwargs:

        Returns:

        """
        return text

    def prehistory_recept(self, userdialog):
        """
        Prehistory recept is not imp[;lemented for TextReceptor because it greedy consumes text
        :return: tuple (is_recepted, results)
        """

        return False, None


class PatternedTextSlot(FreeTextSlot):
    """
    Slot which validates answer by patterns in regexp
    """
    patterns = ListField(DynamicField(required=False))

    meta = {
        "allow_inheritance": True
    }

    def recept(self, text, *args, **kwargs):
        """
        Method that actually recepts message and extracts Slot's Value from it

        Args:
            text: text to be analyzed (str)
            *args:
            **kwargs:

        Returns:

        """
        import re
        for int_pat in self.patterns:
            match = re.search(int_pat, text, flags=re.IGNORECASE)
            if match:
                # import ipdb; ipdb.set_trace()

                #value_meta = {
                #     "triggered_pattern": int_pat,
                #     # "match": match,
                #     "matched_text_segment": match[0],
                #     "value": match[1]
                #
                #}
                return match[1]

        return False

    def can_recept(self, text, *args, **kwargs):
        """
        Method that checks if UserMessage can be recepted by Receptor

        :param text:
        :param args:
        :param kwargs:
        :return: True/False

        """
        if self.recept(text, *args, **kwargs):
            return True
        else:
            return False


class CategoricalSlot(BaseSlot):
    """
    Slot which restricts domain of values of the slot to a set of nominal categories.

    Each category is specified with synset (as list of strings)
    """
    # categories_synsets: dictionary of categories, each category maps into lexical values.
    # if param is None then asserted that parent provides this specification.
    categories_synsets = DynamicField(default={})
    # Example of format:
    # domain_of_values_synsets = {
    #     ANSWER_YES: [
    #         "ДА", "Yes", "Sim", "да", "Да", "Конечно", "Наверное", "Вероятно", "Ок",
    #
    #     ],
    #     ANSWER_NO: [
    #         "НЕТ", "НЕ", "нет", "Нет", "не", "Вряд ли", "Едва ли", "Сомневаюсь", "Ни за что"
    #
    #     ],
    # }

    meta = {
        "allow_inheritance": True
    }

    def can_recept(self, text, *args, **kwargs):
        """
        Method that checks if UserMessage can be recepted by Receptor

        :param text:
        :param args:
        :param kwargs:
        :return: True/False
        # TODO partial reception of the message!
        """
        for each_cur in self.text2category_index.keys():
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
        for each_cur in self.text2category_index.keys():
            if each_cur.lower() in text.lower():
                results.append(self.text2category_index[each_cur])

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

        # import ipdb; ipdb.set_trace()

        usermessages = userdialog.list_user_messages()
        # search for the recent slot setting (from recent messages to oldest):
        for each_msg in reversed(usermessages):
            can_rec = self.can_recept(each_msg)
            if can_rec:
                results = self.recept(each_msg)
                return can_rec, results

        return False, None

    def _make_inverted_index(self):
        # index for resolving text into category:
        self._text2category_index = {}

        for canonic_name, synset in self.categories_synsets.items():
            for each_syn in synset:
                self._text2category_index[each_syn] = canonic_name

        return self._text2category_index
    @property
    def text2category_index(self):
        """

        Returns: dict

        """
        if not hasattr(self, '_text2category_index'):
            self._text2category_index = self._make_inverted_index()
        return self._text2category_index

#
# class CategoricalRegExpSlot(CategoricalSlot):
#     """
#     Categorical slot which allows regular expressions in synsets specification
#     """
#     def can_recept(self, text, *args, **kwargs):
#         """
#         Method that checks if UserMessage can be recepted by Receptor
#
#         :param text:
#         :param args:
#         :param kwargs:
#         :return: True/False
#         # TODO partial reception of the message!
#         """
#         for each_cur in self.text2category_index.keys():
#             if each_cur.lower() in text.lower():
#                 return True
#
#         else:
#             return False
#
#     def recept(self, text, *args, **kwargs):
#         """
#         Method that actually recepts message and extracts Slot's Value from it
#         :param text:
#         :param args:
#         :param kwargs:
#         :return:
#         """
#         results = []
#         for each_cur in self.text2category_index.keys():
#             if each_cur.lower() in text.lower():
#                 results.append(self.text2category_index[each_cur])
#
#         if results:
#             # we have something in results
#             print("DictionarySlotReceptorMixin.recept: %s grasped results: %s" % (self, results))
#             # TODO make productions signals?
#         return results
#
#     def prehistory_recept(self, userdialog):
#         """
#         Method launched after interaction triggering to consume User's directive about time without explicit question
#
#         In this case we may use the same methods of extraction, although in general case
#         Prehistory Analysis differs from ExplicitQuestioningAnswer Analysis
#
#         Returns only the most recent match!
#
#         :return: tuple (is_recepted, results)
#         """
#         # get text of prehistory
#         # grasp datetimes mentioned before, the most recent datetimes are more confident estimations
#
#         # import ipdb; ipdb.set_trace()
#
#         usermessages = userdialog.list_user_messages()
#         # search for the recent slot setting (from recent messages to oldest):
#         for each_msg in reversed(usermessages):
#             can_rec = self.can_recept(each_msg)
#             if can_rec:
#                 results = self.recept(each_msg)
#                 return can_rec, results
#
#         return False, None


########DEPRECATED##########################################################################################
##################################################################################################
# class CategoricalSlotField(BaseSlot):
#     """
#     Abstraction of Categorical Slot
#     """
#
#     def __init__(self, name, questioner=None, domain_of_values_synsets=None, target_uri=None,
#                  silent_value=None, confirm_silent_value=False,
#                  slot_process_specification_class=None,
#                  requestioning_strategy=REQUESTIONING_STRATEGY_DEFAULT):
#         """
#         A factory method for categorical slots
#
#         :param name: reference name for registry
#         :param target_uri: reference name for URI of slot value in the memory, if None then the same as @name used
#         :param silent_value: value that is used if no information was provided by user initiative (or default value)
#         :param confirm_silent_value: should slot process request confirmation from user about silent value (if user have not provided value explicitly)
#         :param questioner: question string (or questioning function for template based questions)
#
#         :param domain_of_values_synsets: for dictionary based slots we need to specify domain of values and their synonyms
#         :param slot_process_specification_class: SlotProcess specifies ReAskingStrategy, PreHistory analysis
#             default is SlotProcess
#         :param prehistory_extractor_spec: class which may be called before explicit question is asked
#             (for filling slot value from dialog prehistory, when user initiates slot filling without questioning,
#             this method may implement different algorithm in comparison to ActiveQuestioningProcess Receptor)
#         :param requestioning_strategy: may be Greed, Passive, ResumeOnIdle
#         :return: UsableSlot
#
#         # TODO WARNING if you patch this class with complex prehistory receptors (which depends on other methods)
#         you need to import other methods as weel as method prehistory_recept, recept, can_recept.
#
#         """
#
#         self.name = name
#         self.target_uri = target_uri or name
#         self.silent_value = silent_value
#         self.confirm_silent_value = confirm_silent_value
#         self.questioner = questioner
#
#         self.domain_of_values_synsets = domain_of_values_synsets
#
#         self.requestioning_strategy = requestioning_strategy
#
#         # # TODO in future:
#         from interactions.models import UserSlotProcess
#         if slot_process_specification_class != UserSlotProcess:
#             raise Exception("Not implemented functionality (UserSlotProcess as slot_process_specification_class is supported only now!)")
#
#         self.flat_norm = ReceptorFactory.synsets_to_flat_norm_index(self.domain_of_values_synsets)
#
#     #### implementation
#     def can_recept(self, text, *args, **kwargs):
#         return self.receptor_spec.can_recept(self, text, *args, **kwargs)
#
#     def recept(self, text, *args, **kwargs):
#         return self.receptor_spec.recept(self, text, *args, **kwargs)
#
#     def prehistory_recept(self, userdialog):
#         pass


# Receptors Base Classes:
class CategoricalReceptorMixin():
    """
    MixIn Class that helps dictionary-based slots to recept UserMessages (in natural language)
    Currently only case insensitive matching supported!

    Mixin Requires `synset` attribute to be specified in instance
    """
    # children must specify domain of distinctive slot values classes
    CANONIC_DOMAIN = []
    #
    # # children must define flat norm (Dictionary that provides <surface token> to <canonic form> index
    # text2category_index = {}

    # # TODO add support of MultiCase, Stemming support etc
    # # def __init__(self, canonic_domain):

    def _make_flat_norm(self):
        # construct flat norm
        # index object for translating synonyms into normalized categories:

        self.flat_norm = {}
        for canonic_name, synset in self.synsets.items():
            for each_syn in synset:
                self.flat_norm[each_syn] = canonic_name

    def __init__(self, categories_synsets=None):
        """

        Args:
            categories_synsets: dictionary of categories, each category maps into lexical values.
            if param is None then asserted that parent provides this specification.

            Example:
                categories_synsets = {
                    ANSWER_YES: [
                        "ДА", "Yes", "Sim", "да", "Да", "Конечно", "Наверное", "Вероятно", "Ок",

                    ],
                    ANSWER_NO: [
                        "НЕТ", "НЕ", "нет", "Нет", "не", "Вряд ли","Едва ли", "Сомневаюсь","Ни за что"

                    ],
                }
        """
        if categories_synsets:
            self.synsets = categories_synsets

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


class YesNoReceptorMixin(CategoricalReceptorMixin):
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

    def __init__(self, categories_synsets=None):
        if not categories_synsets:
            categories_synsets = self.synsets
        super().__init__(categories_synsets=categories_synsets)

    def prehistory_recept(self, userdialog):
        """Disable prehistory recepting for default Yes/No, otherwise we may catch irrelevant Yes/No answers"""
        # import ipdb; ipdb.set_trace()

        return False, None

################################################################################################

### Drafts:
#
# class DictionaryBasedSlotField(BaseSlot):
#     """
#
#         Dictionary based slot uses CANONIC_NAMES list as domain of distinct value classes.
#
#         Each Canonic Name (name of the SlotValueClass) should be supported with Synsets (all possible lexical
#         representations of the values in the UserMessage for matching the ValueClass).
#
#         TODO we may need to introduce additional layer of abstraction with normalized synonyms (words in normal form)
#         So the alogithm during pattern matching phase will match normal form in Specification with SurfaceForm of Word
#         (in particular tense, modality, number etc). Currently we allow only strict match
#
#
#         Slot with target_uri specification
#     """
#     def __init__(self, name, domain_of_values_synsets=None, receptor_spec=None, target_uri=None,
#                  silent_value=None, confirm_silent_value=False, questioner=None,
#                  slot_process_specification_class=None,
#                  requestioning_strategy=REQUESTIONING_STRATEGY_DEFAULT):
#         """
#         A factory method for dictionary based slots
#
#         :param name: reference name for registry
#         :param target_uri: reference name for URI of slot value in the memory, if None then the same as @name used
#         :param silent_value: value that is used if no information was provided by user initiative (or default value)
#         :param confirm_silent_value: should slot process request confirmation from user about silent value (if user have not provided value explicitly)
#         :param questioner: question string (or questioning function for template based questions)
#         :param receptor_spec: UserMessageReceptor specification, mixin class for recepting slot value
#
#         :param domain_of_values_synsets: for dictionary based slots we need to specify domain of values and their synonyms
#         :param slot_process_specification_class: SlotProcess specifies ReAskingStrategy, PreHistory analysis
#             default is SlotProcess
#         :param prehistory_extractor_spec: class which may be called before explicit question is asked
#             (for filling slot value from dialog prehistory, when user initiates slot filling without questioning,
#             this method may implement different algorithm in comparison to ActiveQuestioningProcess Receptor)
#         :param requestioning_strategy: may be Greed, Passive, ResumeOnIdle
#         :return: UsableSlot
#
#         # TODO WARNING if you patch this class with complex prehistory receptors (which depends on other methods)
#         you need to import other methods as weel as method prehistory_recept, recept, can_recept.
#
#         """
#
#         self.name = name
#         self.target_uri = target_uri or name
#         self.silent_value = silent_value
#         self.confirm_silent_value = confirm_silent_value
#         self.questioner = questioner
#
#         self.domain_of_values_synsets = domain_of_values_synsets
#
#         # receptor spec must provide methods recept(text, *, **) and can_recept(text, *, **)
#         self.receptor_spec = receptor_spec
#
#         self.requestioning_strategy = requestioning_strategy
#
#         # # TODO in future:
#         from interactions.models import UserSlotProcess
#         if slot_process_specification_class != UserSlotProcess:
#             raise Exception("Not implemented functionality (UserSlotProcess as slot_process_specification_class is supported only now!)")
#
#         self.flat_norm = ReceptorFactory.synsets_to_flat_norm_index(self.domain_of_values_synsets)
#
#     def can_recept(self, text, *args, **kwargs):
#         return self.receptor_spec.can_recept(self, text, *args, **kwargs)
#
#     def recept(self, text, *args, **kwargs):
#         return self.receptor_spec.recept(self, text, *args, **kwargs)
#
#
# class ReceptorFactory():
#     """
#     Constructs a pair of receptor function (SlotReceptorMixin) + domain of allowed values
#     """
#     @classmethod
#     def make_receptor(cls, receptor_template_class, domain_of_values_synsets):
#         """
#         Constructs a Receptor Instance which may be mixed into slot declaration
#         :param receptor_template_class:
#         :param domain_of_values_synsets:
#         :return:
#         """
#         receptor_mixin_instance = receptor_template_class()
#         receptor_mixin_instance.CANONIC_DOMAIN = domain_of_values_synsets.keys()
#         receptor_mixin_instance.synsets = domain_of_values_synsets
#         receptor_mixin_instance.flat_norm = ReceptorFactory.synsets_to_flat_norm_index(domain_of_values_synsets)
#         return receptor_mixin_instance
#
#     @classmethod
#     def synsets_to_flat_norm_index(cls, domain_of_values_synsets):
#         """
#         :param domain_of_values_synsets:
#
#         Converts dictionary of domain values like
#         domain_of_values_synsets =
#         {
#             CANONIC_NAME1: [synonym1, synonym2, ...]
#             CANONIC_NAME2: [synonym21, synonym22, ...]
#         }
#         into
#
#         text2category_index =
#         {
#             synonym1: CANONIC_NAME1
#             synonym2: CANONIC_NAME1
#             synonym21: CANONIC_NAME2
#             synonym22: CANONIC_NAME2
#         }
#
#         :return: text2category_index
#         """
#         flat_norm = {}
#         for canonic_name, synset in domain_of_values_synsets.items():
#             for each_syn in synset:
#                 flat_norm[each_syn] = canonic_name
#
#         return flat_norm
#
#
# class ReceptorInterface():
#     """
#     Class for description of scheme of Receptors
#     """
#     def can_recept(self, text, *args, **kwargs):
#         """
#
#         Args:
#             text:
#             *args:
#             **kwargs:
#
#         Returns:
#
#         """
#         raise Exception("Implement me!")
#
#     def recept(self, text, *args, **kwargs):
#         """
#
#         Args:
#             text:
#             *args:
#             **kwargs:
#
#         Returns:
#
#         """
#         raise Exception("Implement me!")
#
#     def prehistory_recept(self, userdialog):
#         """
#
#         Args:
#             userdialog:
#
#         Returns:
#
#
#         """
#         raise Exception("Implement me!")