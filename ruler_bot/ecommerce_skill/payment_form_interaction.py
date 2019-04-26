from components.interactions.models import SlottyFormInteraction
from components.slots.slots_factory import SlotsFactory
from mongoengine import *


class PaymentFormInteraction(SlottyFormInteraction):
    # special slot for payment type, we check it in decisioning what to do next (Which payment
    # form to push into agenda):
    payment_type_slot = GenericReferenceField()

    PAY_BY_CARD = 'Оплата картой'
    PAY_BY_CASH = 'Оплата наличными'
    payment_types_choices = [PAY_BY_CARD, PAY_BY_CASH]

    # structure which holds slots for each available payment type:
    slots_for_payment_types = MapField(ListField(GenericReferenceField()))
    """
    This slotty form implements form for payment info specification.

    It has the following scenario:
    1. Request evaluation of payment type slot from user (payment_type_slot).
        Available payment types are:
            Pay by card
            Pay by cash
    2. Depending on value of payment_type_slot
    2.1 If value of payment_type_slot is Pay by card then start form filling process
        and collect slots of carnumber, cardholder, expire_date, cvc code (;))
        2.1.1 After filling slots push order into EShopOrders API
    2.2 If value of payment_type_slot is Pay by cash then push order into EShopOrders API
    """

    @classmethod
    def make_slottfy_form(cls, name):
        """
        Constructor to create a form. Currently it is not flexible at all and adding new payment
        types requires new class implementation.
        Args:
            name:

        Returns:

        """
        # create slots
        # create slot for type

        # very simple generation of lexical forms:
        categories_and_synsets = {
            cls.PAY_BY_CARD: ["картой", "карта"],
            cls.PAY_BY_CASH: ["нал", "кеш"],
        }

        payment_types_slot = SlotsFactory.produce_categorical_slot(
            "payment_types_slot",
            f"Какой способ оплаты вас интересует? Возможные варианты: {cls.payment_types_choices}",
            categories_domain_specification=categories_and_synsets)

        # cash payment does not require any further form filling process and we can complete
        # interaction
        declared_slots = [payment_types_slot]
        cards_slot = cls._slots_for_card_payment()
        declared_slots += cards_slot

        # TODO implement polymorphic slotty forms that allow to evaluate subforms?

        sf, _ = cls.get_or_create(name=name, declared_slots=declared_slots, payment_type_slot=payment_types_slot)
        return sf

    @classmethod
    def _slots_for_card_payment(cls):
        """

        Returns: slots list for card payment type

        """

        card_number_slot = SlotsFactory.produce_free_text_slot("card_number_slot",
                                                               "Напишите номер вашей карты?")
        card_cvc_code_slot = SlotsFactory.produce_free_text_slot("card_cvc_code_slot",
                                                                 "Напишите CVC код вашей карты?")
        cardholder_name_slot = SlotsFactory.produce_free_text_slot("cardholder_name_slot",
                                                                   "Напишите имя владельца карты?")
        card_valid_until_slot = SlotsFactory.produce_free_text_slot("card_valid_until_slot",
                                                                    "Напишите месяц и год до которых валидна карта?")

        # ######################################################################################
        slots = [card_number_slot, card_cvc_code_slot, cardholder_name_slot, card_valid_until_slot]
        return slots

    def start(self, *args, **kwargs):
        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm
        # if not hasattr(self, 'ic'):
        udm.DialogPlanner.sendText(
            "Начинаем слотовую форму")

        udm.DialogPlanner.remind_retrospect_or_retrieve_slot(
            slot_spec_name=self.payment_type_slot.get_name(),
            target_uri=self.payment_type_slot.get_name(),
            callback=self.on_payment_type_chosen,
            priority="URGENT"
        )

    def on_payment_type_chosen(self, *args, **kwargs):
        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm

        payment_type_slot_value = udm.MemoryManager.get_slot_value(self.payment_type_slot.get_name())
        assert len(payment_type_slot_value)==1
        payment_type_slot_value = payment_type_slot_value[0]

        if payment_type_slot_value == self.PAY_BY_CASH:
            # TODO make separate exit gates for different output types?
            # if client chosen pay by cash no more information we need we can complete interaction
            udm.DialogPlanner.sendText("PAY BY CASH is chosen")
            udm.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)
        elif payment_type_slot_value == self.PAY_BY_CARD:
            udm.DialogPlanner.sendText("PAY BY CARD is chosen")
            card_slots = self._slots_for_card_payment()

            for every_slot in card_slots:
                udm.DialogPlanner.remind_retrospect_or_retrieve_slot(
                    slot_spec_name=every_slot.get_name(),
                    target_uri=every_slot.get_name(),
                    callback=self.on_some_slots_filled,
                    priority="URGENT"
                )

        else:
            raise Exception("Unrecognized state!")

    def on_some_slots_filled(self, *args, **kwargs):
        print("SlottyFormInteraction:Some slots filled!")
        filled_slots_values = {}
        unfilled_slots = []
        # TODO remove hack of dynamic attaching of information controller
        kwargs['user_slot_process'].user_domain.reload()
        udm = kwargs['user_slot_process'].user_domain.udm

        # detect filled and unfilled slots
        for each_slot in self.declared_slots:
            slot_val = udm.MemoryManager.get_slot_value_quite(each_slot.name)
            if not slot_val:
                unfilled_slots.append(each_slot)
            else:
                filled_slots_values[each_slot] = slot_val

        if unfilled_slots:
            # not all slots filled, then we need to select next unfilled slot
            # TODO implement complex policy to support A&B|C problem
            print("UNFILLED SLOTS:")
            print(unfilled_slots)

        else:
            # import ipdb; ipdb.set_trace()
            # discponnect all slots?
            # announce completion!
            # run submit action?
            # print("COMPLETING SLOTTY FORM")
            udm.DialogPlanner.sendText("Your payment information is collected")
            udm.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)
