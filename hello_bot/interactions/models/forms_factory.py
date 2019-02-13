from interactions.models import AbstractInteraction, Interaction


# class SlottyFormInteraction(AbstractInteraction):
class SlottyFormInteraction(Interaction):
    def __init__(self, name, slots):
        super().__init__()
        self.name = name
        self.declared_slots = slots


    # @classmethod
    # def initialize(cls, ic, name=None, *args, **kwargs):
    #     """
    #     Interaction initialization requres:
    #     1. specify its name (And register it in the Interactions Registry)
    #     2. initilize EXIT GATES of the interaction.
    #         EXIT GATES are declared in implementation class, if not then default set of exit gates is assumed
    #         (the only: ExitGate_Ok)
    #
    #     :param ic:
    #     :param name:
    #     :param args:
    #     :param kwargs:
    #     :return:
    #     """
    #
    #     if not name:
    #         # default name is a name of class
    #         name = cls.__name__
    #
    #     intrctn, _ = cls.objects.get_or_create(name=name)
    #
    #     intrctn.ic = ic
    #
    #     # #########################################################################################
    #     # # Exit Gate Signals and Registry initialization
    #     intrctn.EXIT_GATES_SIGNALS = {}
    #
    #     if not hasattr(intrctn, 'EXIT_GATES_NAMES_LIST'):
    #         # TODO fix to support inheritance of ExitGates!
    #         # then import default Gates :
    #         intrctn.EXIT_GATES_NAMES_LIST = cls.base_EXIT_GATES_NAMES_LIST
    #
    #     # now init signal objects for each exit gate:
    #     for each_exit_gate_name in intrctn.EXIT_GATES_NAMES_LIST:
    #         # create a signal object for each exit gate
    #         intrctn.EXIT_GATES_SIGNALS[each_exit_gate_name] = django.dispatch.dispatcher.Signal(
    #             providing_args=["userdialog"])
    #
    #     intrctn._anti_garbage_collector_callbacks_list = []
    #     # END ExitGate Signals Initialization
    #
    #     ########################################################################################
    #     intrctn.post_init_hook()
    #
    #     return intrctn

    def start(self, *args, **kwargs):
        # activate interaction if it is not activated
        # run prehistory analysis
        # get list of unfilled slots
        # run process for the first pending required slot
        # on some slot filled route to the policy for chosing next slot
        # super().start(*args, **kwargs)
        for every_slot in self.declared_slots:
            self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(
                slot_spec_name=every_slot.get_name(),
                target_uri=every_slot.get_name(),
                callback=self.on_some_slots_filled)

    def on_some_slots_filled(self, *args, **kwargs):
        print("Some slots filled!")
        filled_slots_values = {}
        unfilled_slots = []
        for each_slot in self.declared_slots:
            slot_val = self.ic.MemoryManager.get_slot_value_quite(each_slot.name)
            if not slot_val:
                unfilled_slots.append(each_slot)
            else:
                filled_slots_values[each_slot] = slot_val
        # import ipdb; ipdb.set_trace()
        if unfilled_slots:
            # not all slots filled, then we need to select next unfilled slot
            # TODO implement complex policy to support A&B|C problem
            print("UNFILLED SLOTS:")
            print(unfilled_slots)
            next_slot = unfilled_slots[0]
            self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(
                slot_spec_name=next_slot.get_name(),
                target_uri=next_slot.get_name(),
                callback=self.on_some_slots_filled, priority="URGENT")
        else:
            # import ipdb; ipdb.set_trace()
            # discponnect all slots?
            # announce completion!
            # run submit action?
            print("COMPLETING SLOTTY FORM")
            self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)
            print("KEKEKEKEKEKE")

