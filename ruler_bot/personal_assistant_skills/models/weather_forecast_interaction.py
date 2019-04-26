# -*- coding: utf-8 -*-
from mongoengine import StringField

from components.slots.city_slot import CitySlot
from components.slots.datetime_slot import DateTimeSlot

from components.interactions.models import Interaction


class WeatherForecastDateSlot(DateTimeSlot):
    name = StringField(default='WeatherForecastDateSlot')

    questioner = StringField(default="Погода на какой день интересует вас?")


class WeatherForecastCitySlot(CitySlot):
    name = StringField(default='WeatherForecastCitySlot')

    questioner = StringField(default="В каком городе?")


class WeatherForecastInteraction(Interaction):
    """
    Interaction with GlobalReceptor Detecting the command about Weather Request
    """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)

    @property
    def location_slot_instance(self):
        # import ipdb; ipdb.set_trace()

        wf_location_slot, _ = WeatherForecastCitySlot.get_or_create()
        return wf_location_slot

    @property
    def date_slot_instance(self):
        wf_date_slot, _ = WeatherForecastDateSlot.get_or_create()
        return wf_date_slot

    def connect_to_dataflow(self, udc):
        """
        The post-initialize hook  for attaching global receptors.

        Here we connect the interaction's Global Receptors with InformationController
        :return:
        """
        self._connect_receptor(receptor_type="PhrasesMatcher",
                               init_args={'phrases': ["What is the weather in *",
                                                      "Gimme weather", "Will it rain?",
                                                      "Give me forecast for tomorrow",
                                                      "ПОГОДА",
                                                      "КАКАЯ ПОГОДА",
                                                      ]},
                               callback_fn=self.start)



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
        super().start(*args, **kwargs)
        print(kwargs)
        assert 'user_domain' in kwargs
        ud = kwargs['user_domain']

        ud.udm.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=self.location_slot_instance.get_name(),
                                                   target_uri=self.location_slot_instance.get_name(),
                                                   callback=self.on_some_slots_filled, priority="URGENT")

        ud.udm.DialogPlanner.remind_retrospect_or_retrieve_slot(slot_spec_name=self.date_slot_instance.get_name(),
                                                   target_uri=self.date_slot_instance.get_name(),
                                                   callback=self.on_some_slots_filled, priority="URGENT")

    def on_some_slots_filled(self, *args, **kwargs):
        """
        Check if both slots are filled, if so calls WeatherService Request
        :param args:
        :param kwargs:
        :return:
        """
        # import ipdb; ipdb.set_trace()

        print(kwargs)
        assert 'user_domain' in kwargs
        ud = kwargs['user_domain']

        date_raw = ud.udm.MemoryManager.get_slot_value_quite(self.date_slot_instance.name)
        loc_raw = ud.udm.MemoryManager.get_slot_value_quite(self.location_slot_instance.name)
        if date_raw is None or loc_raw is None:
            return
        else:
            response_text = self.weather_request(date_raw, loc_raw)
            ud.udm.DialogPlanner.sendText(response_text)

            ud.udm.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)

    def weather_request(self, date_raw, loc_raw):
        # forecast_text = "Weather Forecast in %s %s: " % (loc_raw[0], date_raw["value"])
        # Uncomment the next code if you want to enable remote HTTP weather service:
        forecast_text = "Weather will be okay."
        # forecast_text = self._weather_service_now(loc_raw)

        if forecast_text:
            response_text = "Weather Forecast in %s %s:\n%s" % (loc_raw[0], date_raw["value"], forecast_text)
        else:
            response_text = "Something goes wrong with weather service :("
        return response_text

    def _weather_service_now(self, city_name):
        # http://dpk.io/services/weather/moscow
        URL = "http://dpk.io/services/weather/%s" % city_name
        import requests as req

        resp = req.get(URL)
        print(resp.text)
        # import ipdb; ipdb.set_trace()
        return resp.text


