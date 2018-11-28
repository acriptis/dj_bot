# -*- coding: utf-8 -*-
from components.matchers.matchers import TrainigPhrasesMatcher
from interactions.models import Interaction, AbstractInteraction
import django.dispatch


class WeatherForecastInteraction(Interaction, AbstractInteraction):
    """
    Interaction with GlobalReceptor Detecting the command about Weather Request
    """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)
        super(AbstractInteraction, self).__init__()

    def post_init_hook(self):
        """
        The post-initialize hook  for attaching global receptors.

        Here we connect the interaction's Global Receptors with InformationController
        :return:
        """
        # this Interaction may be activated by Receptor (actually it is binary intent classifier here)
        self.global_trigger_receptor = TrainigPhrasesMatcher(training_phrases=["What is the weather in *",
                                                                                  "Gimme weather", "Will it rain?",
                                                                                  "Give me forecast for tomorrow",
                                                                                  "ПОГОДА",
                                                                                  "КАКАЯ ПОГОДА",
                                                                                  "\Weather"
                                                                                  ],
                                                                daemon_if_matched=self.start)
        self.ic.user_message_signal.connect(self.global_trigger_receptor)

        self._prepare_slots()
        # register slots:
        # register LocationSlot with default value = Moscow
        # register DateSlot with default value = now
        # but slot processe must use following priorities for choosing the values:
        # 1 if nothing provided use default slot value
        # 2 if prehistory contains slot value choose preanswered slot value
        # 3 as explicitly the value of slot for which case?
        # register slots:

    def _prepare_slots(self):
        """
        Constructs and registers slots dynamically
        :return:
        """
        # ##########################################################################################################
        # construct LocationSlot
        from components.slots.slots import DictionarySlotReceptorMixin
        from interactions.models import UserSlotProcess
        from components.slots.slots import DictionaryBasedSlotField
        self.location_slot_instance = DictionaryBasedSlotField(
            # reference name for registry
            name="DynamicLocationSlot",

            # for dictionary based slots we need to specify domain of values and their synonyms:
            domain_of_values_synsets={
                "МОСКВА": ["МОСКВА", "МСК", "ДЕФОЛТ-СИТИ", "МОСКВЕ"],
                "БОБРУЙСК": ["БОБРУЙСК", "БОБ"]
            },
            # UserMessageReceptor specification:
            # mixin class for recepting slot
            receptor_spec=DictionarySlotReceptorMixin,

            # value that is used if no information was provided by user initiative (or default value)
            silent_value=None,
            # should slot process request confirmation from user about silent value (if user have not provided value explicitly)
            confirm_silent_value=False,

            # question string:
            questioner="В каком городе?",

            # END UserMessageReceptor specification:

            # slot process specifies ReAskingStrategy, PreHistory analysis
            slot_process_specification_class=UserSlotProcess
        )

        # first we need to register the slot by name:
        self.ic.sm.register_slot(self.location_slot_instance)
        # import ipdb; ipdb.set_trace()

        # END construct LocationSlot
        # ##########################################################################################################
        # ##########################################################################################################
        # DATERANGE SLOT
        self.date_slot_instance = DictionaryBasedSlotField(
            # reference name for registry
            name="DynamicDateSlot",

            # for dictionary based slots we need to specify domain of values and their synonyms:
            domain_of_values_synsets={
                "СЕГОДНЯ": ["СЕГОДНЯ", "сегодня"],
                "ЗАВТРА": ["ЗАВТРА", "завтра"]
            },
            # UserMessageReceptor specification:
            # mixin class for recepting slot
            receptor_spec=DictionarySlotReceptorMixin,

            # value that is used if no information was provided by user initiative (or default value)
            silent_value="завтра",
            # should slot process request confirmation from user about silent value (if user have not provided value explicitly)
            confirm_silent_value=False,

            # question string:
            questioner="Когда?",

            # END UserMessageReceptor specification:

            # slot process specifies ReAskingStrategy, PreHistory analysis
            slot_process_specification_class=UserSlotProcess
        )
        self.ic.sm.register_slot(self.date_slot_instance)

    def start(self, *args, **kwargs):
        # if we here means we catched command to get weather forecast.
        # So we need to goalize slots of Location and Date
        # Both slots may have default values (or preloaded from user profile)
        # Both slots may be featured with confirmation interaction
        # Both Slots must be autofilled if user has specified the information before
        self.ic.retrospect_or_retrieve_slot(self.location_slot_instance, target_uri=self.location_slot_instance.name)


        self.ic.retrospect_or_retrieve_slot(self.date_slot_instance, target_uri=self.date_slot_instance.name,
                                            callback=self.weather_request)
        pass

    def weather_request(self, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        # TODO normalize dates
        # TODO normalize cities slot

        date_raw = self.ic.MemoryManager.get_slot_value_quite(self.date_slot_instance.name)
        loc_raw = self.ic.MemoryManager.get_slot_value_quite(self.location_slot_instance.name)

        self.ic.DialogPlanner.sendText("I've checked weather in %s %s: Weather will be okay!" % (loc_raw[0], date_raw[0]))
        return

