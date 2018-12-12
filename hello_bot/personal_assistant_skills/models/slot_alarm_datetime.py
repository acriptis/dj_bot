from components.slots.datetime_slot import DateTimeSlot


class AlarmDateTimeSlot(DateTimeSlot):
    """
    Slot for requesting and infiltrating time of alarm to be set

    """

    name = 'AlarmDateTimeSlot'

    questioner = "На какое время установить будильник?"

