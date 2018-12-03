# -*- coding: utf-8 -*-
from components.matchers.matchers import TrainigPhrasesMatcher
from interactions.models import Interaction, AbstractInteraction

from personal_assistant_interactions.models.slot_alarm_datetime import AlarmDateTimeSlot


class AlarmSetterInteraction(Interaction, AbstractInteraction):
    """
    Interaction with GlobalReceptor Detecting the command about Setting Alarm

    Alarm has
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
        self.global_trigger_receptor = TrainigPhrasesMatcher(training_phrases=["MAKE ALARM",
                                                                                  "SET REMINDER",
                                                                                  "SET ALARM",
                                                                                  "НАПОМИНАЛКА",
                                                                                  "НАПОМИНАЛКУ",
                                                                                  "УСТАНОВИ БУДИЛЬНИК",
                                                                                  "/SetAlarm"
                                                                                  ],
                                                                daemon_if_matched=self.start)

        # TODO add support of triggers:
        # установи будильник на 16 20
        # включи будильник в 4 35
        # напомни мне сварить кашу через 2 часа 15 минут
        # напомни написать письмо научному руководителю завтра
        # напомни написать письмо научному руководителю в обед
        # установи напоминалку сходить в бассейн в субботу вечером
        # установи напоминалку сходить в бассейн на 4 апреля

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


    def start(self, *args, **kwargs):
        # if we here means we catched command to get weather forecast.
        # So we need to goalize slots of Location and Date
        # Both slots may have default values (or preloaded from user profile)
        # Both slots may be featured with confirmation interaction
        # Both Slots must be autofilled if user has specified the information before
        # self.ic.remind_retrospect_or_retrieve_slot(self.location_slot_instance, target_uri=self.location_slot_instance.name)


        self.ic.remind_retrospect_or_retrieve_slot(self.alarm_timestamp_at_slot.name, target_uri=self.alarm_timestamp_at_slot.name,
                                        callback=self.when_alarm_time_ready)
        pass

    def when_alarm_time_ready(self, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        # print("KEKEKEKEK")
        at_datetime = kwargs['results']['value']
        self._set_alarm(at_datetime)

    def _set_alarm(self, at_datetime, title=None):

        self.ic.DialogPlanner.sendText("Я устанавливаю будильник на %s" % (at_datetime))
        return

    def _prepare_slots(self):
        """
        Constructs and registers slots dynamically
        :return:
        """
        self.alarm_timestamp_at_slot = AlarmDateTimeSlot()
        self.ic.sm.register_slot(self.alarm_timestamp_at_slot)
        # ##########################################################################################################
        # construct LocationSlot
        from components.slots.slots import DictionarySlotReceptorMixin
        from interactions.models import UserSlotProcess
        from components.slots.slots import DictionaryBasedSlotField

        # # Experimental code
        # self.alarm_title_slot_instance = FreeTextSlotField(
        #     # reference name for registry
        #     name="AlarmTitleSlot",
        #
        #     # UserMessageReceptor specification:
        #     # mixin class for recepting slot
        #     receptor_spec=FreeTextSlotReceptorMixin,
        #
        #     # value that is used if no information was provided by user initiative (or default value)
        #     silent_value="",
        #     # should slot process request confirmation from user about silent value (if user have not provided value explicitly)
        #     confirm_silent_value=False,
        #
        #     # question string:
        #     questioner="О чем нужно напомнить?",
        #
        #     # END UserMessageReceptor specification:
        #
        #     # slot process specifies ReAskingStrategy, PreHistory analysis
        #     slot_process_specification_class=UserSlotProcess
        # )
        #
        # # first we need to register the slot by name:
        # self.ic.sm.register_slot(self.alarm_title_slot_instance)
        # # import ipdb; ipdb.set_trace()

        # END construct LocationSlot
        # ##########################################################################################################
        # ##########################################################################################################
        # DATERANGE SLOT
        # self.date_time_slot_instance = FuzzyDateTimeSlotField(
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
        #
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
        # self.ic.sm.register_slot(self.date_slot_instance)
        pass
