from components.user_processes.user_slot_process import UserSlotProcess


class UserSlotProcessesManager():
    """
    Manages UserSlotProcesses in Runtime
    Helps to solve signal persistence problem

    Manages UserSlotProcesses and UserSlots?
    """
    def __init__(self, ic):
        self.ic = ic

    def get_or_create_user_slot_process(self, slot_obj, target_uri):
        """
        Interface method useful for
            requesting slot value by slotname through UserSlotProcess (completed
            UserSlotProcess contains attribute with results of evaluation) or
            for attaching callbacks

        This method does not starts the process!

        Args:
            slot_obj: Slot object is Scheme of Slot which holds name, questioner and
            implementation of receptor.

        Returns:
            tuple: (user_slot_process_obj:UserSlotProcess, is_created:bool)

            `is created` marks if the UserSlotProcess is existing process (is_created is False)
            or newly created (is_created is True)
        """
        # TODO handle multiuser case!?
        # TODO add persistency support through db!
        # Requirement: Signals and callbacks must be persistent
        usp = self.find_user_slot_process(slot_obj, target_uri)
        if usp:
            created = False
        else:
            # create
            usp = UserSlotProcess.initialize(self.ic.user_domain, slot_obj, target_uri=target_uri)
            # usp.save()
            created = True

        return usp, created

    def find_user_slot_process(self, curr_slot_obj, target_uri=None):
        """
        Returns related UserSlotProcess (if exist) or None
        :param curr_slot_obj: Slot instance
        :return: UserSlotProcess or None
        """
        if target_uri:
            usps = UserSlotProcess.objects(slot=curr_slot_obj, user_domain=self.ic.user_domain, target_uri=target_uri)
        else:
            usps = UserSlotProcess.objects(slot=curr_slot_obj, user_domain=self.ic.user_domain)
        if usps:
            # return first
            return usps[0]

        return None
