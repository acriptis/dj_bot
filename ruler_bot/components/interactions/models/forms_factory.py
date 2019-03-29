from components.interactions.models import Interaction
from mongoengine import *


class SlottyFormInteraction(Interaction):
    declared_slots = ListField(GenericReferenceField())

    @classmethod
    def make_slottfy_form(cls, name, slots):
        # return cls(name=name, declared_slots=slots)
        sf, _ = cls.get_or_create(name=name, declared_slots=slots)
        return sf

    def connect_to_dataflow(self, ic):
        """
        Connection to DataFlow triggers the interaction to create Signals according
        to Interactions Interface
        Args:
            ic:

        Returns:

        """
        self.ic = ic
        self.EXIT_GATES_SIGNALS = {}
        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        from components.signal_pattern_reflex.signal import Signal
        self.EXIT_GATES_SIGNAL_PATTERNS = {}

        if not hasattr(self, 'EXIT_GATES_NAMES_LIST'):
            # TODO fix to support inheritance of ExitGates!
            # then import default Gates :
            self.EXIT_GATES_NAMES_LIST = self.base_EXIT_GATES_NAMES_LIST

        # now init signal objects for each exit gate:
        for each_exit_gate_name in self.EXIT_GATES_NAMES_LIST:
            # create a signal object for each exit gate
            self.EXIT_GATES_SIGNAL_PATTERNS[
                each_exit_gate_name], _ = SignalPattern.get_or_create_strict(
                signal_type="InteractionProcessCompletedSignal", interaction=self,
                exit_gate=each_exit_gate_name
            )
            self.EXIT_GATES_SIGNALS[each_exit_gate_name] = Signal(signal_type="InteractionProcessCompletedSignal", interaction=self,
                exit_gate=each_exit_gate_name)

        self._anti_garbage_collector_callbacks_list = []
        # END ExitGate Signals Initialization

        self.post_init_hook()

    def start(self, *args, **kwargs):
        # activate interaction if it is not activated
        # run prehistory analysis
        # get list of unfilled slots
        # run process for the first pending required slot
        # on some slot filled route to the policy for chosing next slot
        # super().start(*args, **kwargs)
        # import ipdb; ipdb.set_trace()

        user_domain = kwargs['user_domain']
        self.ic = user_domain.udm
        # if not hasattr(self, 'ic'):
        # self.ic.DialogPlanner.sendText(
        #     "Начинаем слотовую форму")

        for every_slot in self.declared_slots:
            self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(
                slot_spec_name=every_slot.get_name(),
                target_uri=every_slot.get_name(),
                callback=self.on_some_slots_filled,
                priority="URGENT"
            )

    def on_some_slots_filled(self, *args, **kwargs):
        print("SlottyFormInteraction:Some slots filled!")
        filled_slots_values = {}
        unfilled_slots = []
        # TODO remove hack of dynamic attaching of information controller
        if not hasattr(self, 'ic'):
            kwargs['user_slot_process'].user_domain.reload()
            self.ic = kwargs['user_slot_process'].user_domain.udm

        # detect filled and unfilled slots
        for each_slot in self.declared_slots:
            slot_val = self.ic.MemoryManager.get_slot_value_quite(each_slot.name)
            if not slot_val:
                unfilled_slots.append(each_slot)
            else:
                filled_slots_values[each_slot] = slot_val
        # import ipdb; ipdb.set_trace()
        if unfilled_slots:
            #import ipdb; ipdb.set_trace()

            # not all slots filled, then we need to select next unfilled slot
            # TODO implement complex policy to support A&B|C problem
            print("UNFILLED SLOTS:")
            print(unfilled_slots)
            # next_slot = unfilled_slots[0]
            # self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(
            #     slot_spec_name=next_slot.get_name(),
            #     target_uri=next_slot.get_name(),
            #     callback=self.on_some_slots_filled, priority="URGENT")

            # # Dont connect callbacks twice!
            # self.ic.DialogPlanner.remind_retrospect_or_retrieve_slot(
            #     slot_spec_name=next_slot.get_name(),
            #     target_uri=next_slot.get_name(),
            #     priority="URGENT")
        else:
            # import ipdb; ipdb.set_trace()
            # discponnect all slots?
            # announce completion!
            # run submit action?
            # print("COMPLETING SLOTTY FORM")
            self.ic.DialogPlanner.complete_user_interaction_proc(self, exit_gate=self.EXIT_GATE_OK)
