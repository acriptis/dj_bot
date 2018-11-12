# -*- coding: utf-8 -*-
import django.dispatch

from components.dialog_planner import DialogPlanner
from components.memory_manager import MemoryManager


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

