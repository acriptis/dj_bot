# -*- coding: utf-8 -*-
from components.matchers.matchers import PhrasesMatcher
from components.slots.city_slot import CitySlot
from components.slots.datetime_slot import DateTimeSlot

# from interactions.models import Interaction, AbstractInteraction
from interactions.models import Interaction


class WeatherForecastDateSlot(DateTimeSlot):
    name = 'WeatherForecastDateSlot'

    questioner = "Погода на какой день интересует вас?"


class WeatherForecastCitySlot(CitySlot):
    name = 'WeatherForecastCitySlot'

    questioner = "В каком городе?"


class WeatherForecastInteraction(Interaction):
    """
    Interaction with GlobalReceptor Detecting the command about Weather Request
    """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)
        # super(AbstractInteraction, self).__init__()

    def post_init_hook(self):
        """
        The post-initialize hook  for attaching global receptors.

        Here we connect the interaction's Global Receptors with InformationController
        :return:
        """
        ############### Prepare RECEPTOR #################################################
        # this Interaction may be activated by Receptor (actually it is binary intent classifier here)
        self.global_trigger_receptor = PhrasesMatcher(phrases=["What is the weather in *",
                                                                                  "Gimme weather", "Will it rain?",
                                                                                  "Give me forecast for tomorrow",
                                                                                  "ПОГОДА",
                                                                                  "КАКАЯ ПОГОДА",
                                                               "\Weather"
                                                               ],
                                                      daemon_if_matched=self.start)
        # connect receptor:
        self.ic.user_message_signal.connect(self.global_trigger_receptor, weak=False)

        self._prepare_slots()

    def _prepare_slots(self):
        """
        Constructs and registers slots dynamically
        :return:
        """
        # ##########################################################################################################
        # LOCATION SLOT
        self.location_slot_instance = WeatherForecastCitySlot()
        # first we need to register the slot in RunTime system
        self.ic.sm.register_slot(self.location_slot_instance)

        # ##########################################################################################################
        # # DATERANGE SLOT
        self.date_slot_instance = WeatherForecastDateSlot()
        self.ic.sm.register_slot(self.date_slot_instance)

    def start(self, *args, **kwargs):
        """
        # if we here means we catched command to get weather forecast.
        # So we need to goalize slots of Location and Date
        # Both slots may have default values (or preloaded from user profile)
        # Both slots may be featured with confirmation interaction
        # Both Slots must be autofilled if user has specified the information before
        :param args:
        :param kwargs:
        :return:
        """
        # inits UserInteraction
        super(self.__class__, self).start(*args, **kwargs)

        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=self.location_slot_instance.get_name(),
                                                   target_uri=self.location_slot_instance.get_name(),
                                                   callback=self.on_some_slots_filled, priority="URGENT")

        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=self.date_slot_instance.get_name(),
                                                   target_uri=self.date_slot_instance.get_name(),
                                                   callback=self.on_some_slots_filled, priority="URGENT")

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
            self.weather_request(date_raw, loc_raw)
            self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)

    def weather_request(self, date_raw, loc_raw):
        # forecast_text = "Weather Forecast in %s %s: " % (loc_raw[0], date_raw["value"])
        # Uncomment the next code if you want to enable remote HTTP weather service:
        forecast_text = "Weather will be okay."
        # forecast_text = self._weather_service_now(loc_raw)

        if forecast_text:
            self.ic.DialogPlanner.sendText("Weather Forecast in %s %s:\n%s" % (loc_raw[0], date_raw["value"], forecast_text))
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
