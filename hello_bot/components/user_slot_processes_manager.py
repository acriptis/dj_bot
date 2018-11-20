from interactions.models.user_slot_process import UserSlotProcess


class UserSlotProcessesManager():
    """
    Manages UserSlotProcesses
    Helps to solve signal persistence problem

    Manages UserSlotProcesses and UserSlots?

    In database we don't store listeners of the slot process.
    So restoring of the instance from DB drops all listeners.
    This issues a problem that callbacks which were attached before are not triggered
    """
    def __init__(self, ic):
        self.ic = ic
        # virtual db for slot processes:
        self.user_slot_processes = {}
        # ^^ keys are slot names and values are UserSlotProcess objects

    def get_or_create_user_slot_process(self, slot_obj):
        """
        Interface method for requesting slot value by slotname through UserSlotProcess and for attaching callback

        This method does not starts the process!
        :param user:
        :param slot_codename:
        :return:
        """

        # TODO handle multiuser case!
        # TODO add persistency support through db!
        # Requirement: Signals and callbacks must be persistent
        slot_codename = slot_obj.get_name()
        if slot_codename in self.user_slot_processes.keys():
            # get
            usp = self.user_slot_processes[slot_codename]
            created = False
        else:
            # create
            usp = UserSlotProcess.initialize(self.ic.user, slot_obj)
            # usp.save()
            created = True
            # put to user slot processes registry:
            self.user_slot_processes[slot_codename] = usp
        return usp, created

    def find_user_slot_process(self, curr_slot_obj):
        """
        Returns related UserSlotProcess (if exist) or None
        :param curr_slot_obj: Slot instance
        :return:
        """
        if curr_slot_obj.get_name() in self.user_slot_processes:
            return self.user_slot_processes[curr_slot_obj.get_name()]
        else:
            return None
