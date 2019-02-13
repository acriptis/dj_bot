
# TODO refactor with real city gazetter
from components.slots.slots import BaseSlotField, CategoricalReceptorMixin


class CitySlot(BaseSlotField, CategoricalReceptorMixin):
    name = 'CitySlot'

    questioner = "В каком городе?"

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
