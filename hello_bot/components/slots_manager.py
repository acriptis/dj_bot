from bank_interactions.models.slots import DesiredCurrencySlot, OptionIntentsSlot, NeedListDocsAndTarifsSlot, \
    ClientServiceRegionSlot, ClientIsResidentRFSlot, ClientPropertyTypeSlot, ClientAgreeWithServicePackConditionsSlot, \
    ClientOkToSelfServiceSlot, ClientIsReadyToGiveDocsSlot, ClientWantsNearestOfficeRecomendation


class SlotsManager():
    """
    The most of scenaric slots are singletons within dialog session

    So the Manager offers interface for all components to retrieve actual version of slot instance from
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

        }
        self.slotClass2SlotNameRouter = {val: key for key, val in self.classname2class.items()}

        # interactions instances registry
        self.classname2instance = {}
        # TODO consider a case when one classname may be derived into multiple instances
        # for non-singleton slots

        # slot_name -> user_slot_process
        self.user_slots = {}

    def get_or_create_instance_by_classname(self, classname):
        """
        Interface method for retrieving INSTANCE by (class)NAME of slot
        Given a classname it returns instance
        :param classname:
        :return:
        """
        if classname in self.classname2instance.keys():
            return self.classname2instance[classname]
        else:
            # get class spec by name

            if classname not in self.classname2class.keys():

                import ipdb; ipdb.set_trace()
                # investigate
                raise Exception("Name %s is not in SlotsManager.classname2class registry" % classname)
            slot_class_spec = self.classname2class[classname]

            return self._initialize_slot(slot_class_spec)

    def get_or_create_instance_by_class(self, slot_class_spec):
        """
        Interface method  for retrieving INSTANCE by CLASS of slot
        Given a class it returns instance
        :param slot_class_spec:
        :return: slot instance
        """
        name = slot_class_spec.get_name()
        return self.get_or_create_instance_by_classname(name)

    def _initialize_slot(self, slot_class_spec):
        """
        Initializes interaction, no existence check
        adds instance to registry
        :param slot_class_spec:
        :return:
        """
        # slot_instance = slot_class_spec.initialize(self.ic)
        slot_instance = slot_class_spec()
        self.classname2instance[slot_instance.get_name()] = slot_instance
        return slot_instance
