from bank_interactions.models.slots import DesiredCurrencySlot, OptionIntentsSlot, NeedListDocsAndTarifsSlot, \
    ClientServiceRegionSlot, ClientIsResidentRFSlot, ClientPropertyTypeSlot, ClientAgreeWithServicePackConditionsSlot, \
    ClientOkToSelfServiceSlot, ClientIsReadyToGiveDocsSlot, ClientWantsNearestOfficeRecomendation
from personal_assistant_skills.models import AlarmDateTimeSlot


class SlotsManager():
    """
    The most of scenaric slots are singletons within dialog session

    So the Manager provides interface for all components to retrieve actual version of slot's schema instance from
        string name,
        class

    It keeps registry of all instantiated, evaluated slots
    """
    def __init__(self, ic):

        self.ic = ic

        # TODO derive base class!
        # TODO remove hardcode!
        # TODO add feature of Slots autodiscovery
        self.classname2class = {
            "DesiredCurrencySlot": DesiredCurrencySlot,
            "OptionIntentsSlot": OptionIntentsSlot,
            "NeedListDocsAndTarifsSlot": NeedListDocsAndTarifsSlot,
            "ClientIsResidentRFSlot": ClientIsResidentRFSlot,
            "ClientServiceRegionSlot": ClientServiceRegionSlot,
            "ClientPropertyTypeSlot": ClientPropertyTypeSlot,
            "ClientAgreeWithServicePackConditionsSlot": ClientAgreeWithServicePackConditionsSlot,
            "ClientOkToSelfServiceSlot": ClientOkToSelfServiceSlot,
            "ClientIsReadyToGiveDocsSlot": ClientIsReadyToGiveDocsSlot,
            "ClientWantsNearestOfficeRecomendation": ClientWantsNearestOfficeRecomendation,
            "AlarmDateTimeSlot": AlarmDateTimeSlot,

        }
        self.slotClass2SlotNameRouter = {val: key for key, val in self.classname2class.items()}

        # slot instances registry
        self.slotname2instance = {}
        # TODO consider a case when one classname may be derived into multiple instances
        # for non-singleton slots

        # slot_name -> user_slot_process
        self.user_slots = {}


    def get_or_create_instance_by_slotname(self, slotname):
        """
        Interface method for retrieving INSTANCE by SLOTNAME (or CLASSNAME of slot)
        Given a classname it returns instance
        :param slotname:
        :return:
        """
        if slotname in self.slotname2instance.keys():
            return self.slotname2instance[slotname]
        else:
            # get class spec by name

            if slotname not in self.classname2class.keys():

                import ipdb; ipdb.set_trace()
                # investigate
                raise Exception("Name %s is not in SlotsManager.classname2class registry" % slotname)
            slot_class_spec = self.classname2class[slotname]

            return self._initialize_slot(slot_class_spec)

    def get_or_create_instance_by_class(self, slot_class_spec):
        """
        Interface method  for retrieving INSTANCE by CLASS of slot
        Given a class it returns instance
        :param slot_class_spec:
        :return: slot instance
        """
        # name = slot_class_spec.get_name()
        name = slot_class_spec.name
        return self.get_or_create_instance_by_slotname(name)

    def _initialize_slot(self, slot_class_spec):
        """
        Initializes interaction, no existence check
        adds instance to registry
        :param slot_class_spec:
        :return:
        """
        # slot_instance = slot_class_spec.initialize(self.ic)
        slot_instance = slot_class_spec()
        self.register_slot(slot_instance)
        return slot_instance

    def register_slot(self, slot_spec_obj):
        """
        Registers slot in registry so the same slot reference may be used for accessing evaluated data by any
        Interaction.

        If slot is already in registry it jsut returns True


        Expects slot to have get_name() method for accessing shared name

        :param slot_spec_obj: instance of SlotField subclass

        :return: tuple (slot_name, slot_instance)
        """

        # name of slot which may be a name of class or particular name (for  MultiSlot dialog )
        slot_name = slot_spec_obj.get_name()
        if  slot_name not in self.slotname2instance:
            self.slotname2instance[slot_name] = slot_spec_obj
        return slot_name, slot_spec_obj


#     def compose_dynamic_slot_schema(self, target_uri, questioner, receptor_class, reasking_strategy="Greed", memory_target_uri=None, *args, **kwargs):
#         """
#         Factory method for construction of a custom slot according to
#         slot configuration specification
#
#         name - name of slot
#         questioner - string or callable returning string with question about slot
#         receptor class - mixin class providin recept and can_recept methods for filling the slot
#             from user response
#         reasking_strategy - specification of behaviour for cases when user don't answer the question
#
#
#         return slot object
#
#         """
#         target_uri, slot_type, asker_fn, receptor_fn, validator_fn, normalizer_fn,
#
#         #              required, elicitable, *args, **kwargs
#         # attrs to be provided
#         # name
#         # receptor_object
#         # questioner
#
#         pass
#
#
# def make_custom_dynamic_slot():
#
#     target_uri = "desired_currency"
#     question = "Какая Валюта?"
#
#     def recept(text):
#         if "USD" in text:
#             return "USD"
#         else:
#             return None
#
#     def can_recept(text):
#         if "USD" in text:
#             return True
#         else:
#             return None
#
#     sm = SlotsManager(None)
#     slot_schema = sm.compose_dynamic_slot_schema(target_uri=target_uri, questioner=question, can_recept_fn =can_recept, recept_fn=recept)
#
#     # initilization
#     slot_spec_instance = slot_schema()
#
#     # register slot instance in slots manager
#     slot_spec_instance
#
#     # then we may push it into process