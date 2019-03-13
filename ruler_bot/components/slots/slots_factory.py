from components.slots.slots import BaseSlotField, \
    CategoricalReceptorMixin, YesNoReceptorMixin, FreeTextSlot


class SlotsFactory():
    """
    Bunch of factory methods to create a Slot instances retrievable
    by Interactions from UserDialog

    TODO: should factory make registration of object?

    """

    @classmethod
    def produce_categorical_slot(cls, name, questioner, categories_domain_specification,
                                 requestioning_strategy="ResumeOnIdle", reuse=True,
                                 silent_value=None):
        """
        factory method for production of unregistered slots with categorical values

        Args:
            name: name of slot
            questioner:
            categories_domain_specification:
            TODO specify format
            requestioning_strategy:
        """
        # cat_slot = BaseSlotField()
        # cat_slot.name = name
        # cat_slot.questioner = questioner
        # cat_slot.requestioning_strategy = requestioning_strategy
        #
        # cat_slot.domain_of_values_synsets = categories_domain_specification
        #
        # mixin_instance = CategoricalReceptorMixin(categories_synsets=categories_domain_specification)
        #
        # cat_slot.recept = mixin_instance.recept
        # cat_slot.can_recept = mixin_instance.can_recept
        #
        # # if prehistory reception available?
        # cat_slot.prehistory_recept = mixin_instance.prehistory_recept

        #################################################
        from components.slots.slots import CategoricalSlot
        if not reuse:

            slot = CategoricalSlot(name=name, questioner=questioner, silent_value=silent_value,
                                   categories_synsets=categories_domain_specification).save()
        else:
            slot, created = CategoricalSlot.get_or_create(
                name=name, questioner=questioner, silent_value=silent_value,
                categories_synsets=categories_domain_specification)
        return slot


    @classmethod
    def produce_yes_no_slot(cls, name, questioner, requestioning_strategy="ResumeOnIdle"):
        """
        factory method for production of unregistered slots with YesNo Receptor

        Args:
            name:
            questioner:
            requestioning_strategy:
        """
        cat_slot = BaseSlotField()
        cat_slot.name = name
        cat_slot.questioner = questioner
        cat_slot.requestioning_strategy = requestioning_strategy

        cat_slot.domain_of_values_synsets = YesNoReceptorMixin.synsets

        mixin_instance = YesNoReceptorMixin()

        cat_slot.recept = mixin_instance.recept
        cat_slot.can_recept = mixin_instance.can_recept

        # if prehistory reception available?
        cat_slot.prehistory_recept = mixin_instance.prehistory_recept

        return cat_slot

    @classmethod
    def produce_free_text_slot(cls, name, questioner, reuse=True):
        """

        factory method for production of unregistered slots with FreeText Receptor (consumes any input)

        Args:
            name:
            questioner:
            reuse: bool: if True then system does not declares duplicated slots, and uses existing

        Returns: Slot instance which may be used in dialog process

        """
        if not reuse:
            slot = FreeTextSlot(name=name, questioner=questioner).save()
        else:
            slot, created = FreeTextSlot.get_or_create(name=name, questioner=questioner)
        return slot

    @classmethod
    def produce_patterned_text_slot(cls, name, questioner, validative_regexp_patterns, reuse=True):
        """
        Produces slot which consumes text answers with pattern validation
        Args:
            name:
            questioner:
            validative_regexp_patterns:
            reuse:

        Returns:

        """
        # TODO refactor me
        from components.slots.slots import PatternedTextSlot
        if not reuse:
            slot = PatternedTextSlot(name=name, questioner=questioner,
                                     patterns=validative_regexp_patterns).save()
        else:
            slot, created = PatternedTextSlot.get_or_create(name=name, questioner=questioner,
                                                            patterns=validative_regexp_patterns)
        return slot

    @classmethod
    def produce_username_text_slot(cls, name, questioner, validative_regexp_patterns=None, reuse=True):
        """
        Factory method to produce slot for Person Name retrieving in russian
        Args:
            name:
            questioner:
            validative_regexp_patterns:
            reuse:

        Returns:

        """

        if not validative_regexp_patterns:
            validative_regexp_patterns = [
                "Меня зовут (.+)",
                "Можешь звать меня (.+)",
                "зови меня (.+)",
                "Я (.+)",
                # "(. +)",
            ]
        return cls.produce_patterned_text_slot(name, questioner, validative_regexp_patterns, reuse)


    # def make_slot(self, name="CustomSlot", target_uri=None, silent_value=None, confirm_silent_value=None, questioner=None,
    #               receptor_spec=None, domain_of_values_synsets={}, slot_process_specification_class=None,
    #               prehistory_extractor_fn=None
    #               ):
    #     """
    #     A factory method for dictionary based slots
    #
    #     Args:
    #         name: reference name for registry
    #
    #         target_uri: reference name for URI of slot value in the memory, if None then the same as @name used
    #
    #         silent_value: value that is used if no information was provided by user initiative (or default value)
    #
    #         confirm_silent_value: should slot process request confirmation from user about silent value (if user have not provided value explicitly)
    #
    #         questioner: question string (or questioning function for template based questions)
    #
    #         receptor_spec: UserMessageReceptor specification, mixin class for recepting slot value
    #
    #         domain_of_values_synsets: for dictionary based slots we need to specify domain of values and their synonyms
    #
    #         slot_process_specification_class: SlotProcess specifies ReAskingStrategy, PreHistory analysis
    #             default is SlotProcess
    #
    #         prehistory_extractor_fn: method which may be called before explicit question is asked
    #         (for filling slot value by message said by user)
    #
    #     Returns:
    #         usable slot instance
    #     """
    #     # TODO finish me
    #     slot = BaseSlotField()
    #     slot.name = name
    #
    #     target_uri = target_uri or name
    #     slot.target_uri = target_uri
    #     return slot