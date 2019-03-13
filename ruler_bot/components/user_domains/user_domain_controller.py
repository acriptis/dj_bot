# -*- coding: utf-8 -*-
from components.dialog_management.dialog_planner import DialogPlanner
from components.dialog_management.userdialog import UserDialog
from components.interactions_manager import InteractionsManager
from components.memory_manager import MemoryManager
from components.slots.slots_manager import SlotsManager
from components.user_slot_processes_manager import UserSlotProcessesManager


class ReceptorsPool():
    """
    ReceptorsPool is pool of receptors functions which are
    called on New User Message event
    """
    def __init__(self, ic):
        self.receptors = []
        self.ic = ic

    def connect(self, fn):
        if fn in self.receptors:
            # already exist!
            import ipdb; ipdb.set_trace()

        self.receptors.insert(0, fn)
        self.ic.user_domain.user_message_signal_pattern.connect(fn, weak=False)
        # self.ic.user_domain.user_message_signal.connect(fn, weak=False)
        # TODO SignalReflexRoute
        # srr = SignalReflexRoute(user_domain,
        #          signal={'signal_type': 'UserMessageSignal'},
        #          refllex={'type': 'user_slot_process_method',
        #                   'slot_codename': self.id,
        #                   'method_name': 'on_user_response'}
        #          )

    def disconnect(self, fn):
        self.receptors.remove(fn)
        self.ic.user_domain.user_message_signal_pattern.disconnect(fn)


class UserDomainController():
    """

    aka UserInformationController is a PlugIn for information management,
    may be plugged to an Agent object or to a Skill instance for managing access of
    internal components to information and behaviours of the system.

    each user has its own Information controller
    """

    # TODO design structure
    def __init__(self, user_domain):
        """

        Args:
            user:
        """
        # we need to emulate user context:
        self.user_domain = user_domain

        # actually dialog proxy:
        self.userdialog = UserDialog(self.user_domain.dialog)

        # init DialogPlanner
        self.DialogPlanner = DialogPlanner(self)

        self.MemoryManager = MemoryManager(self)

        # helper for interactions
        self.im = InteractionsManager(self)

        # slot specifications:
        self.sm = SlotsManager(self)

        # slot + user data management:
        self.uspm = UserSlotProcessesManager(self)

        # all interactions and skills must connect its receptors to Receptors Pool
        # for receiving signals of UserMessages
        self.receptors_pool = ReceptorsPool(self)

    def reload(self):
        """reloads internals"""
        self.user_domain.reload()