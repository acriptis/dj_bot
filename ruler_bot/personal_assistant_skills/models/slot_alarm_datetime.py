from components.slots.datetime_slot import DateTimeSlot
from mongoengine import StringField


class AlarmDateTimeSlot(DateTimeSlot):
    """
    Slot for requesting and infiltrating time of alarm to be set

    """

    name = StringField(default='AlarmDateTimeSlot')

    questioner = StringField(default="На какое время установить будильник?")

