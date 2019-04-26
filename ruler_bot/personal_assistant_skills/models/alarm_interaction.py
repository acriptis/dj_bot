# -*- coding: utf-8 -*-
from components.matchers.matchers import PhrasesMatcher
from components.interactions.models import Interaction

from personal_assistant_skills.models.slot_alarm_datetime import AlarmDateTimeSlot


class AlarmSetterInteraction(Interaction):
    """Interaction with GlobalReceptor Detecting the command about Setting Alarm
    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Interaction, self).__init__(*args, **kwargs)

    def connect_to_dataflow(self, udc):
        """
        The post-initialize hook  for attaching global receptors.

        Here we connect the interaction's Global Receptors with InformationController
        :return:
        """
        # TODO add support of triggers:
        # установи будильник на 16 20
        # включи будильник в 4 35
        # напомни мне сварить кашу через 2 часа 15 минут
        # напомни написать письмо научному руководителю завтра
        # напомни написать письмо научному руководителю в обед
        # установи напоминалку сходить в бассейн в субботу вечером
        # установи напоминалку сходить в бассейн на 4 апреля
        self._connect_receptor(receptor_type="PhrasesMatcher",
                               init_args={'phrases': ["MAKE ALARM",
                                                               "SET REMINDER",
                                                               "SET ALARM",
                                                               "НАПОМИНАЛКА",
                                                               "НАПОМИНАЛКУ",
                                                               "УСТАНОВИ БУДИЛЬНИК",
                                                               "/SetAlarm"
                                                               ]},
                               callback_fn=self.start)

    @property
    def alarm_timestamp_at_slot(self):
        # import ipdb; ipdb.set_trace()

        alarm_timestamp_at_slot, _ = AlarmDateTimeSlot.get_or_create()
        return alarm_timestamp_at_slot

    def start(self, *args, **kwargs):
        super().start(*args, **kwargs)
        # if we here means we catched command to get weather forecast.
        # So we need to goalize slots of Location and Date
        # Both slots may have default values (or preloaded from user profile)
        # Both slots may be featured with confirmation interaction
        # Both Slots must be autofilled if user has specified the information before
        # self.ic.remind_retrospect_or_retrieve_slot(self.location_slot_instance, target_uri=self.location_slot_instance.name)

        self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(self.alarm_timestamp_at_slot.name,
                                                                 target_uri=self.alarm_timestamp_at_slot.name,
                                                                 callback=self.when_alarm_time_ready,
                                                                 priority="URGENT")
        pass

    def when_alarm_time_ready(self, *args, **kwargs):
        print(kwargs)
        assert 'user_domain' in kwargs
        ud = kwargs['user_domain']
        # import ipdb; ipdb.set_trace()

        datetime_raw = ud.udm.MemoryManager.get_slot_value_quite(self.alarm_timestamp_at_slot.name)
        at_datetime = datetime_raw['value']

        # #################################################################################
        # ## Behavior Actualization:  #####################################################
        ud.udm.DialogPlanner.sendText("Я устанавливаю будильник на %s" % (at_datetime))
        # #################################################################################

        # should we complete interaction  before alarm has triggered?
        ud.udm.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)
