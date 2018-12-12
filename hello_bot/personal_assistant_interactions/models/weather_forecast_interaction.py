# -*- coding: utf-8 -*-

from components.matchers.matchers import TrainigPhrasesMatcher
from components.slots.city_slot import CitySlot
from components.slots.datetime_slot import DateTimeSlot

from interactions.models import Interaction, AbstractInteraction


class WeatherForecastDateSlot(DateTimeSlot):
    name = 'WeatherForecastDateSlot'

    questioner = "Погода на какой день интересует вас?"


class WeatherForecastCitySlot(CitySlot):
    name = 'WeatherForecastCitySlot'

    questioner = "В каком городе?"


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
        # connect receptor:
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
        # self.location_slot_instance = DictionaryBasedSlotField(
        #     # reference name for registry
        #     name="DynamicLocationSlot",
        #
        #     # for dictionary based slots we need to specify domain of values and their synonyms:
        #     domain_of_values_synsets={
        #         "moscow": ["МОСКВА", "МСК", "ДЕФОЛТ-СИТИ", "МОСКВЕ"],
        #         "bobruisk": ["БОБРУЙСК", "БОБ"]
        #     },
        #     # UserMessageReceptor specification:
        #     # mixin class for recepting slot
        #     receptor_spec=DictionarySlotReceptorMixin,
        #
        #     # value that is used if no information was provided by user initiative (or default value)
        #     silent_value=None,
        #     # should slot process request confirmation from user about silent value (if user have not provided value explicitly)
        #     confirm_silent_value=False,
        #
        #     # question string:
        #     questioner="В каком городе?",
        #
        #     # END UserMessageReceptor specification:
        #
        #     # slot process specifies ReAskingStrategy, PreHistory analysis
        #     slot_process_specification_class=UserSlotProcess
        # )
        self.location_slot_instance = WeatherForecastCitySlot()

        # first we need to register the slot by name:
        self.ic.sm.register_slot(self.location_slot_instance)
        # import ipdb; ipdb.set_trace()

        # END construct LocationSlot
        # ##########################################################################################################
        # ##########################################################################################################
        # # DATERANGE SLOT
        # self.date_slot_instance = DictionaryBasedSlotField(
        #     # reference name for registry
        #     name="DynamicDateSlot",
        #
        #     # for dictionary based slots we need to specify domain of values and their synonyms:
        #     domain_of_values_synsets={
        #         "СЕГОДНЯ": ["СЕГОДНЯ", "сегодня"],
        #         "ЗАВТРА": ["ЗАВТРА", "завтра"]
        #     },
        #     # UserMessageReceptor specification:
        #     # mixin class for recepting slot
        #     receptor_spec=DictionarySlotReceptorMixin,
        #     # prehistory_extractor_spec=DateTimeSlot,
        #     # value that is used if no information was provided by user initiative (or default value)
        #     silent_value="завтра",
        #     # should slot process request confirmation from user about silent value (if user have not provided value explicitly)
        #     confirm_silent_value=False,
        #
        #     # question string:
        #     questioner="Когда?",
        #
        #     # END UserMessageReceptor specification:
        #
        #     # slot process specifies ReAskingStrategy, PreHistory analysis
        #     slot_process_specification_class=UserSlotProcess
        # )
        self.date_slot_instance = WeatherForecastDateSlot()
        self.ic.sm.register_slot(self.date_slot_instance)

    def start(self, *args, **kwargs):
        # if we here means we catched command to get weather forecast.
        # So we need to goalize slots of Location and Date
        # Both slots may have default values (or preloaded from user profile)
        # Both slots may be featured with confirmation interaction
        # Both Slots must be autofilled if user has specified the information before

        # self.ic.remind_or_retrieve_slot(self.location_slot_instance, target_uri=self.location_slot_instance.name)
        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=self.location_slot_instance.get_name(),
                                                   target_uri=self.location_slot_instance.get_name(),
                                                   callback=self.on_some_slots_filled)

        #
        # self.ic.remind_or_retrieve_slot(self.date_slot_instance,
        #                                 target_uri=self.date_slot_instance.name,
        #                                 callback=self.on_some_slots_filled)
        # import ipdb; ipdb.set_trace()

        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=self.date_slot_instance.get_name(),
                                                   target_uri=self.date_slot_instance.get_name(),
                                                   callback=self.on_some_slots_filled)
        pass

    def on_some_slots_filled(self, *args, **kwargs):
        """
        Check if both slots are filled, if so calls WeatherService Request
        :param args:
        :param kwargs:
        :return:
        """
        date_raw = self.ic.MemoryManager.get_slot_value_quite(self.date_slot_instance.name)
        loc_raw = self.ic.MemoryManager.get_slot_value_quite(self.location_slot_instance.name)
        if date_raw is None or loc_raw is None:
            return
        else:
            self.weather_request()

    def weather_request(self, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        # TODO normalize dates
        # TODO normalize cities slot

        date_raw = self.ic.MemoryManager.get_slot_value_quite(self.date_slot_instance.name)
        loc_raw = self.ic.MemoryManager.get_slot_value_quite(self.location_slot_instance.name)
        forecast_text = "I've checked weather in %s %s: Weather will be okay!" % (loc_raw[0], date_raw["value"])
        # Uncomment the next code if you want to enable remote HTTP weather service:
        # forecast_text = self._weather_service_now(loc_raw)

        if forecast_text:
            self.ic.DialogPlanner.sendText("Weather report for %s %s:\n%s" % (loc_raw[0], date_raw["value"], forecast_text))
        else:
            self.ic.DialogPlanner.sendText("Something goes wrong with weather service :(")
        return

    def _weather_service_now(self, city_name):
        # http://dpk.io/services/weather/moscow
        URL = "http://dpk.io/services/weather/%s" % city_name
        import requests as req

        resp = req.get(URL)
        print(resp.text)
        # import ipdb; ipdb.set_trace()
        return resp.text
