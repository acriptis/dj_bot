# -*- coding: utf-8 -*-
import django.dispatch

from components.dialog_planner import DialogPlanner
from components.interactions_manager import InteractionsManager
from components.memory_manager import MemoryManager
from components.slots_manager import SlotsManager
from components.user_slot_processes_manager import UserSlotProcessesManager


class InformationController():

    # TODO design structure
    def __init__(self, user=None):
        # we need to emulate user context:
        if user:
            self.user = user
        else:
            self.user = "Греф"



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

