
# TODO refactor with real city gazetter
from mongoengine import StringField, DynamicField

from components.slots.slots import CategoricalSlot


class CitySlot(CategoricalSlot):

    ######################################################
    # Slot's Values Domain Specification
    MSK = "Moscow"
    BOBRU = "Bobruisk"
    CANONIC_DOMAIN = [MSK, BOBRU]

    # lookup tables?
    # synonyms set + gazetter:
    synsets = {
        MSK: [
            "МОСКВА", "МСК", "ДЕФОЛТ-СИТИ", "МОСКВЕ"
        ],
        BOBRU: [
            "БОБРУЙСК", "БОБРУИСК", "БОБ"
        ]

    }
    name = StringField(default='CitySlot')

    categories_synsets = DynamicField(default=synsets)

    questioner = StringField(default="В каком городе?")
