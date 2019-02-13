from bank_consulter_skill.models import IntentRetrievalInteraction, DesiredCurrencyInteraction, \
    DocumentsListSupplyInteraction, PrivateInfoFormInteraction, BusinessOfferingInteraction, GreetingInteraction, \
    ConsideringSelfServiceInteraction, OnlineReservingFinalizationInteraction, OfficeRecommendationInteraction, \
    DialogTerminationInteraction, OperatorSwitchInteraction
from interactions.models import SlottyFormInteraction
from introduction_skill.models.introduction_interaction import IntroductionInteraction
from personal_assistant_skills.models import WeatherForecastInteraction, AlarmSetterInteraction
# from persons_skill.persons_interaction import PersonsInteraction

from root_skill.models import ShowMemoryInteraction, ShowAgendaInteraction


class InteractionsManager():
    """
    The most of scenaric interactions are singletons wuithin dialog session

    So the Manager provides interface for all components to retrieve actual version of interaction instance from
        string name,
        class

    It keeps registry of all instantiated interactions
    """
    def __init__(self, ic):

        self.ic = ic

        # TODO derive base class!
        # TODO remove hardcode!
        # TODO add feature of Interactions autodiscovery
        self.classname2class = {
            "GreetingInteraction": GreetingInteraction,
            "IntentRetrievalInteraction": IntentRetrievalInteraction,
            "DesiredCurrencyInteraction": DesiredCurrencyInteraction,
            "DocumentsListSupplyInteraction": DocumentsListSupplyInteraction,
            "PrivateInfoFormInteraction": PrivateInfoFormInteraction,
            "BusinessOfferingInteraction": BusinessOfferingInteraction,
            "ConsideringSelfServiceInteraction": ConsideringSelfServiceInteraction,
            "OnlineReservingFinalizationInteraction": OnlineReservingFinalizationInteraction,
            "OfficeRecommendationInteraction": OfficeRecommendationInteraction,
            "DialogTerminationInteraction": DialogTerminationInteraction,
            "OperatorSwitchInteraction": OperatorSwitchInteraction,

            "WeatherForecastInteraction": WeatherForecastInteraction,

            "AlarmSetterInteraction": AlarmSetterInteraction,

            "ShowMemoryInteraction": ShowMemoryInteraction,
            "ShowAgendaInteraction": ShowAgendaInteraction,
            "IntroductionInteraction": IntroductionInteraction,
            # "SlottyFormInteraction": SlottyFormInteraction,
            # "PersonsInteraction": PersonsInteraction
        }

        # interactions instances registry
        self.interaction_name2instance = {}
        # TODO consider a case when one classname may be derived into multiple instances
        # for non-singleton interactions

    def get_or_create_instance_by_name(self, classname):
        """
        Interface method for retrieving INSTANCE by (class)NAME of interaction
        Given a classname it returns instance
        :param classname:
        :return:
        """
        if classname in self.interaction_name2instance.keys():
            return self.interaction_name2instance[classname]
        else:
            # get class spec by name
            if classname not in self.classname2class.keys():
                raise Exception("Name %s is not in InteractionsManager.classname2class registry" % classname)
            interaction_class_spec = self.classname2class[classname]

            return self._initialize_interaction(interaction_class_spec)

    def get_or_create_instance_by_class(self, interaction_class_spec):
        """
        Interface method  for retrieving INSTANCE by CLASS of interaction
        Given a class it returns instance
        :param interaction_class_spec:
        :return: interaction instance
        """
        name = interaction_class_spec.get_name()
        return self.get_or_create_instance_by_name(name)

    def _initialize_interaction(self, interaction_class_spec):
        """
        Initializes interaction, no existence check
        adds instance to registry
        :param interaction_class_spec:
        :return:
        """
        interaction_instance = interaction_class_spec.initialize(self.ic)
        self.interaction_name2instance[interaction_class_spec.get_name()] = interaction_instance
        return interaction_instance

    def register_interaction(self, interaction_obj):
        """
        Registers interaction in registry so the same interaction reference may be used for
        accessing evaluated data by any Interaction.

        If interaction is already in registry it jsut returns True


        Expects slot to have get_name() method for accessing shared name

        :param slot_spec_obj: instance of SlotField subclass

        :return: tuple (slot_name, slot_instance)
        """

        # name of slot which may be a name of class or particular name (for  MultiSlot dialog )
        interaction_name = interaction_obj.get_name()
        if interaction_name not in self.interaction_name2instance:
            self.interaction_name2instance[interaction_name] = interaction_obj
        return interaction_name, interaction_obj
