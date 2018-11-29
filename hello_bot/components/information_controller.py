# -*- coding: utf-8 -*-
import django.dispatch

from components.dialog_planner import DialogPlanner
from components.interactions_manager import InteractionsManager
from components.memory_manager import MemoryManager
from components.slots.slots_manager import SlotsManager
from components.user_slot_processes_manager import UserSlotProcessesManager
from interactions.models import QuestionInteractionFactory, UserDialog


class InformationController():
    """
    InformationController is a PlugIn for information management, may be plugged to an Agent object or to a Skill
    instance for managing access of internal components to information and behaviours of the system.

    """

    # TODO design structure
    def __init__(self, user=None):
        # we need to emulate user context:
        if user:
            self.user = user
        else:
            self.user = "Греф"

        # create user dialog and push the message
        self.userdialog = UserDialog.objects.create()

        # list of callables which are called at each utterance
        # self.receptors = []
        # here is user-specific receptors!
        # initilize receptors registry
        self.active_receptors = []

        self.global_memory = {}

        # list of responses from interactions:
        self.responses_list = []

        # signal emmitted when user message comes:
        self.user_message_signal = django.dispatch.dispatcher.Signal(providing_args=["userdialog"])
        self.system_production_signal = django.dispatch.dispatcher.Signal(providing_args=["production"])

        # init DialogPlanner
        self.DialogPlanner = DialogPlanner(self)

        self.MemoryManager = MemoryManager(self)

        # helper for interactions
        self.im = InteractionsManager(self)

        # slot specifications:
        self.sm = SlotsManager(self)

        # slot + user data management:
        self.uspm = UserSlotProcessesManager(self)

    def remind_or_retrieve_slot(self, slot_spec, target_uri=None, callback=None, priority=10):
        """
        Interface method for domain interactions which encapsulates slots management as knowledge-agnostic interface
        (Callers of method don't know if the value exist already or must be retrieved through interactive process).
        The system requests slot from memory or by retrieval process and returns result through the callback


        :param slot_spec: class of the Slot to be evaluated
        :param target_uri:
        :return:
        """

        # TODO consider the best placement of this method (possibly in some universe of InformationManager/MemoryManager/SlotsManager/UserSlotsManager/DialogPlanner)
        slot_spec_obj = self.sm.get_or_create_instance_by_class(slot_spec)
        if not target_uri:
            # means uri is slot name for singleton slots
            target_uri = slot_spec_obj.get_name()
        try:
            slot_value = self.MemoryManager.get_slot_value(target_uri)
            # send data to callback
            # may be buggy call...
            callback(slot_value)
        except Exception as e:
            # slot is not available, hence we need to run slot process
            self.DialogPlanner.plan_process_retrieve_slot_value_with_slot_spec_instance(slot_spec_obj, priority=priority, callback_fn=callback, target_uri=target_uri, duplicatable=False)

    def remind_retrospect_or_retrieve_slot(self, slot_spec_name, target_uri=None, callback=None, priority=10):
        """
        Interface method for domain interactions which encapsulates slots management as knowledge-agnostic interface
        (Callers of method don't know if the value exist already or must be retrieved through interactive process).
            The system requests slot from memory,
                if memory check fails
                    the system tries to apply retrospection process
                        (anlyse dialog prehistory to extract slot value from user's initiative directive),
                    if retrospection fails
                        the system launches ActiveQuestioningProcess or default value retrieval

        :param slot_spec_name: Slot name to be evaluated
        :param target_uri:
        :return:
        """

        slot_spec_obj = self.sm.get_or_create_instance_by_slotname(slot_spec_name)
        if not target_uri:
            # means uri is slot name for singleton slots
            target_uri = slot_spec_obj.get_name()
        try:
            slot_value = self.MemoryManager.get_slot_value(target_uri)
            # send data to callback
            # may be buggy call...
            callback(slot_value)
        except Exception as e:
            print("PURUMPUMPUM")
            is_recepted, results = slot_spec_obj.prehistory_recept(self.userdialog)
            if is_recepted:
                print("Recepted Slot from Prehistory!")
                print(results)
            else:
                # enqueue active questioning process
                # slot is not available, hence we need to run slot process
                self.DialogPlanner.plan_process_retrieve_slot_value_with_slot_spec_instance(slot_spec_obj, priority=priority, callback_fn=callback, target_uri=target_uri, duplicatable=False)
