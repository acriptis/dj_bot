from django.db import models
import django.dispatch

from interactions.models import DPUserProfile
from .user_slot import UserSlot


class UserSlotProcess(models.Model):
    """
    The process of interaction between user and system about some slot filling via ActiveQuestioning Process

    TODO link ActiveQuestioningProcess in doc

    For slots that requre asking the user and then handling the answer

    TODO Strategy of requestioning must be attachable composite behaviour
    """
    # slot_filled_signal = django.dispatch.dispatcher.Signal(providing_args=["user_slot_process"])

    INIT = 'Init'
    ACTIVE = 'Active'
    CANCELLED = 'Cancelled'
    COMPLETED = 'Completed'
    IGNORED = 'Ignored'
    INTERACTION_STATES = (
        (INIT, 'init'),
        (ACTIVE, 'Active'),
        (IGNORED, 'Ignored'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
    )

    # ###################################################################################################
    # ######## ORM Attrs ################################################################################
    # user = models.CharField(max_length=200)
    user = models.ForeignKey(DPUserProfile, on_delete=models.CASCADE)

    # we define slots as dynamic classes, so we put class name and then route it into dynamic object:
    slot_codename = models.CharField(max_length=200)

    state = models.CharField(max_length=200, choices=INTERACTION_STATES, default=INIT)
    # ######## END ORM Attrs ################################################################################
    # ###################################################################################################

    @classmethod
    def initialize(cls, user, slot_obj, target_uri=None):
        """
        1. Create UserSlotProcess if it is not exist
        2. Declare Signal of the process for announcing completion (slot_filled_signal)

        :param user:
        :param slot_obj:
        :param target_uri: URI in memory ontology where the value must be written to
        :return:
        """
        # slot_codename = slotClass2SlotNameRouter[slot_obj.__class__]
        slot_codename = slot_obj.get_name()

        usp, _ = cls.objects.get_or_create(user=user, slot_codename=slot_codename)
        # signal emitted when slot is filled
        usp.slot_filled_signal = django.dispatch.dispatcher.Signal(providing_args=["user_slot_process", "results"])
        # TODO how to restore signal connections? (So listeners will be notified)
        usp.slot = slot_obj
        usp.target_uri = target_uri

        # counts for failed recepts (may be used by ReQuestioning Strategy):
        usp.recept_fails_counter = 0

        return usp

    def save(self, *args, **kwargs):
        # return
        # import ipdb; ipdb.set_trace()
        #
        if not hasattr(self, 'slot_codename'):
            # self.slot_codename = slotClass2SlotNameRouter[self.slot.__class__]
            self.slot_codename = self.slot.get_name()
        return super(self.__class__, self).save(*args, **kwargs)

    def start(self, ic):
        """

        Start of ActiveQuestioning retrieval process:
        1. Ask Question to user
        2. Connect AnswerReceptor to UserMessageSignal
        3. Set state as Active
        :param ic:
        :return:
        """
        # TODO implement pre-search that avoids questioning if user provided Answer in Dialog Prehistory

        # send question to active dialog
        self.ic = ic
        # #################################################################################
        # ########## START ACTIVE QUESTIONING PHASE #######################################
        self.ic.userdialog.send_message_to_user(self.slot.asker_fn())

        # tiny check that we don't ask two questions in one step
        if self.ic.DialogPlanner.current_step_active_question:
            # second slot at current step
            # Exceptional case adding the second slot. Is it context switch?
            print(self.ic.DialogPlanner.questions_under_discussion)
            import ipdb; ipdb.set_trace()

        # now we should put the question under questions on dicsussio
        self.ic.DialogPlanner.questions_under_discussion.insert(0, self.slot)
        self.ic.DialogPlanner.current_step_active_question = self.slot

        # connect particular Receptor to ActiveReceptors Pool
        self.ic.user_message_signal.connect(self.on_user_response)
        self.state = self.ACTIVE
        self.save()
        # #################################################################################

    def reasking_process(self):
        """
        function called when ReAsking approved by dialog planner
        :return:
        """
        self.ic.userdialog.send_message_to_user(self.slot.asker_fn())
        self.ic.DialogPlanner.current_step_active_question = self.slot
        # assert that usermessage connector is still connected

    def on_user_response(self, *args, **kwargs):
        """
        When user message comes after questioning
        :param text:
        :return:
        """
        text = kwargs['message']

        if self.slot.can_recept(text):
            result = self.slot.recept(text)
            # #################################################################################
            # ########## FINALIZATION and MEMORIZATION of the SLOT  ###########################
            self.ic.user_message_signal.disconnect(self.on_user_response)
            self.complete_self(result)
            # END FINALIZATION and MEMORIZATION of the SLOT
            # #################################################################################
        else:
            # wrong response (
            self.recept_fails_counter += 1
            self.state = self.IGNORED
            self.save()


            # TODO refactor
            # #################################################################################
            # ########## Requestioning Strategy Exploitation ##################################
            if self.slot.requestioning_strategy == "Greed":

                # Greed reAsk Strategy:
                print("Slot Unhandled (Greed reAsk Strategy). ReAsking...")
                self.ic.userdialog.send_message_to_user(self.slot.asker_fn() + " (Greed ReAsk Strategy)")

                # print("Slot Unhandled (Passive waiting Strategy)")
            elif self.slot.requestioning_strategy == "ResumeOnIdle":
                # self.ic.reaskers_queue.append(self)
                # if self.recept_fails_counter >= 3:
                #     print("Slot Unhandled (ResumeOnIdle). ReAsking...")
                #     self.ic.userdialog.send_message_to_user(self.slot.asker_fn() + " (ResumeOnIdle ReAsk Strategy)")
                pass
            elif self.slot.requestioning_strategy == "Passive":
                # default behaviour?
                print("Slot Unhandled (Passive Strategy)...")
            else:
                raise Exception("Unspecified ReQuestioning Strategy!")
            # TODO implement attachement of Exception Strategy:
            # 1. Forced Slot: ReAsk Urgently
            # 2. Passive Waiting, but we need to attach handler
            # here

    def complete_self(self, result):
        """
        Implements finalization of slot process with provided result
        :param result:
        :return:
        """
        self.result = UserSlot(self.user, self.slot, result)
        # self.result.save()
        self.raw_result = result
        self.state = self.COMPLETED
        if self.target_uri:
            # write the memory
            self.ic.MemoryManager.put_slot_value(self.target_uri, result)

        # now we should remove question under discussion (if we are in active questioning process)
        if self.slot in self.ic.DialogPlanner.questions_under_discussion:
            self.ic.DialogPlanner.questions_under_discussion.remove(self.slot)

        self.slot_filled_signal.send(sender=self, user_slot_process=self, results=result)
        self.save()
        print("User response filled slot %s: %s!" % (self.slot, result))

    def fast_evaluation_process_attempt(self):
        """
        Attempt to evaluate slot without Interacting with User
        :return:
        """
        is_recepted, result = self._fast_evaluation_process_attempt_raw_output()
        if is_recepted and self.state != self.COMPLETED:
            # finlize userslot process (if it is not finalized yet)
            self.complete_self(result)

        return is_recepted, result

    def _fast_evaluation_process_attempt_raw_output(self):
        """
        Process of value evaluation when we check
            1. Memory
            2. Prehistory
            3. DefaultValue

        if some of them succed then annoubnce completion
        else return exception

        No callback polling

        No slot process finalization

        :return: (is_slot_value_retrieved:bool, result:any)
        """
        slot_spec_obj = self.slot

        if not self.target_uri:
            # means uri is slot name for singleton slots
            self.target_uri = slot_spec_obj.get_name()

        try:
            # #######################################################################################
            # ########## MemorySlotValueRetrievalOperation ##########################################
            slot_value = self.ic.MemoryManager.get_slot_value(self.target_uri)

            return True, slot_value

        except Exception as e:
            # #########################################################################
            # ###### PreHistory Filling Process #####################################
            if hasattr(slot_spec_obj, 'prehistory_recept'):
                print("Retrieving slot %s value from PreHistory" % slot_spec_obj)
                # asserting it is callable method!

                is_recepted, results = slot_spec_obj.prehistory_recept(self.ic.userdialog)
                if is_recepted:
                    print("Recepted Slot from Prehistory!")
                    print(results)
                    # if self.target_uri:
                    # write the memory
                    self.ic.MemoryManager.put_slot_value(self.target_uri, results)

                    return True, results

                else:
                    print("Can NOT RECEPT Slot from Prehistory!")
            # no prehistory value, so we need to check default value:
            # #########################################################################
            # ###### Default Value Filling Process #####################################
            if hasattr(slot_spec_obj, 'silent_value') and slot_spec_obj.silent_value:
                # we have default value then we don't need to specify it in ActiveQuestioning
                print("Retrieving slot value from DefaultValue")
                # if self.target_uri:
                # write the memory
                self.ic.MemoryManager.put_slot_value(self.target_uri, slot_spec_obj.silent_value)

                return True, slot_spec_obj.silent_value

            return False, None

    def __str__(self):
        return "User: %s, slot: %s, state: %s" % (self.user, self.slot_codename, self.state)