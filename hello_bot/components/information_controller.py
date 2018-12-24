# -*- coding: utf-8 -*-
import django.dispatch

from components.dialog_planner import DialogPlanner
from components.interactions_manager import InteractionsManager
from components.memory_manager import MemoryManager
from components.slots.slots_manager import SlotsManager
from components.user_slot_processes_manager import UserSlotProcessesManager
from interactions.models import UserDialog


class InformationController():
    """
    InformationController is a PlugIn for information management, may be plugged to an Agent object or to a Skill
    instance for managing access of internal components to information and behaviours of the system.

    """

    # TODO design structure
    def __init__(self, user):
        # we need to emulate user context:

        self.user = user

        # create user dialog and push the message
        # if you want unique dialog for each user uncomment this:
        # self.userdialog, _ = UserDialog.objects.get_or_create(target_user=self.user)

        # if you need new dialog for every session:
        self.userdialog = UserDialog.objects.create(target_user=self.user)

        # list of callables which are called at each utterance
        # self.receptors = []
        # here is user-specific receptors!
        # initilize receptors registry
        self.active_receptors = []

        # signal emmitted when user message comes:
        self.user_message_signal = django.dispatch.dispatcher.Signal(providing_args=["userdialog"])

        # init DialogPlanner
        self.DialogPlanner = DialogPlanner(self)

        self.MemoryManager = MemoryManager(self)

        # helper for interactions
        self.im = InteractionsManager(self)

        # slot specifications:
        self.sm = SlotsManager(self)

        # slot + user data management:
        self.uspm = UserSlotProcessesManager(self)



