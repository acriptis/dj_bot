from mongoengine import Document, StringField, ReferenceField, GenericReferenceField, IntField, DynamicField
from mongoengine.queryset.base import CASCADE
import django.dispatch


# from .user_slot import UserSlot
# from components.user_domains.models import UserDomain


# class UserSlotProcess(Document):
from components.user_processes.user_process import UserProcess
from components.utils.mongoengine_get_or_create_mixin import MongoEngineGetOrCreateMixin


class UserSlotProcess(UserProcess, MongoEngineGetOrCreateMixin):
    """
    The process of interaction between user and system about some slot filling via ActiveQuestioning Process

    TODO link ActiveQuestioningProcess in doc

    For slots that requre asking the user and then handling the answer

    TODO Strategy of requestioning must be attachable composite behaviour
    """
    # ###################################################################################################
    # ######## ORM Attrs ################################################################################
    # we define slots as dynamic classes, so we put class name and then route it into dynamic object:
    slot_codename = StringField(required=False)

    # slot instance:
    slot = GenericReferenceField(required=False)

    # calculates how many times reception attempt failed during ActiveQuestioningProcess:
    recept_fails_counter = IntField(default=0, required=False)
    # (may be used by ReQuestioning Strategy):

    # it is a memory URI where the value of the slot after evaluation will be placed:
    target_uri = StringField(required=False)

    # field for results of evaluation of slot process:
    raw_result = DynamicField(required=False)

    # ######## END ORM Attrs ################################################################################
    # ###################################################################################################

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # get or create NewUserMessage signal

        # self.slot_filled_signal = django.dispatch.dispatcher.Signal(
        #     providing_args=["user_slot_process", "results"])

        # from components.signal_reflex_routes.models.signals import SlotFilledSignal
        # if not self.target_uri:
        #     print(self)
        #     import ipdb; ipdb.set_trace()

        from components.signal_pattern_reflex.signal import Signal
        self.slot_filled_signal = Signal(signal_type="SlotFilledSignal", user_domain=self.user_domain)
        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        self.slot_filled_signal_pattern, _ = SignalPattern.get_or_create_strict(
            signal_type="SlotFilledSignal", user_domain=self.user_domain, slot=self.slot)
        # self.slot_filled_signal.save()

    @classmethod
    def initialize(cls, user_domain, slot_obj, target_uri=None):
        """
        1. Create UserSlotProcess if it is not exist
        2. Declare Signal of the process for announcing completion (slot_filled_signal)

        :param user_domain:
        :param slot_obj:
        :param target_uri: URI in memory ontology where the value must be written to
        :return:
        """
        # slot_codename = slotClass2SlotNameRouter[slot_obj.__class__]
        slot_codename = slot_obj.get_name()

        usp, _ = cls.get_or_create(user_domain=user_domain, slot_codename=slot_codename, slot=slot_obj, target_uri=target_uri)
        # signal emitted when slot is filled

        # # TODO how to restore signal connections? (So listeners will be notified)
        # if user_domain_controller:
        #     usp.ic = user_domain_controller
        return usp

    def connect_to_dataflow(self, user_domain_controller):
        self.ic = user_domain_controller

    def save(self, *args, **kwargs):
        if not hasattr(self, 'slot_codename'):
            # self.slot_codename = slotClass2SlotNameRouter[self.slot.__class__]
            print("Auto creation of attribute slot_codename from classname")
            self.slot_codename = self.slot.get_name()

        return super().save(*args, **kwargs)

    def start(self, ic):
        """

        Start of ActiveQuestioning retrieval process:
        1. Ask Question to user (if it is not asked already on current step)
        2. (GoC)Connect AnswerReceptor to UserMessageSignal
        3. Set state as Active
        :param ic:
        :return:
        """
        # TODO implement pre-search that avoids questioning if user provided Answer in Dialog Prehistory

        # send question to active dialog
        ic.reload()
        self.ic = ic
        # #################################################################################
        # ########## START ACTIVE QUESTIONING PHASE #######################################
        self.ic.DialogPlanner.sendText(self.slot.asker_fn())
        # self.ic.userdialog.send_message_to_user(self.slot.asker_fn())

        # tiny check that we don't ask two questions in one step
        if self.user_domain.agenda.current_step_active_question:
            # second slot at current step
            # Exceptional case adding the second slot. Is it context switch?
            # print(self.ic.DialogPlanner.questions_under_discussion)
            print(self.user_domain.agenda.questions_under_discussion)
            import ipdb; ipdb.set_trace()
            raise Exception("Why 2questions per step?")

        # now we should put the question under questions on discussion
        if self.slot in self.user_domain.agenda.questions_under_discussion:
            print(f"duplicated call to user_slot_process: {self}")
            #self.reload()
            #import ipdb; ipdb.set_trace()
            #print("WTF?")
        else:
            self.user_domain.agenda.questions_under_discussion.insert(0, self.slot)
            self.user_domain.agenda.current_step_active_question = self.slot
            self.user_domain.agenda.save()
            self.user_domain.user_message_signal_pattern.connect(self.on_user_response, weak=False)
        # connect particular Receptor to ActiveReceptors Pool
        # self.user_domain.user_message_signal.connect(self.on_user_response, weak=False)
        self.state = self.ACTIVE
        self.save()
        # #################################################################################

    def reasking_process(self):
        """
        function called when ReAsking approved by dialog planner
        :return:
        """
        # self.user_domain.ic.userdialog.send_message_to_user(self.slot.asker_fn())
        self.user_domain.udm.DialogPlanner.sendText(self.slot.asker_fn())
        self.user_domain.agenda.current_step_active_question = self.slot
        self.user_domain.agenda.save()
        # assert that usermessage connector is still connected

    def on_user_response(self, *args, **kwargs):
        """
        When user message comes after questioning
        :param text:
        :return:
        """
        print("UserSlotProcess.on_user_response")
        text = kwargs['text']
        # import ipdb; ipdb.set_trace()
        if not hasattr(self, 'ic'):
            self.user_domain.reload()

            #from components.user_domains.user_domain_controller import UserDomainController
            self.ic = self.user_domain.udm

        if self.slot.can_recept(text):


            result = self.slot.recept(text)
            # #################################################################################
            # ########## FINALIZATION and MEMORIZATION of the SLOT  ###########################
            # self.user_domain.user_message_signal.disconnect(self.on_user_response)
            self.user_domain.user_message_signal_pattern.disconnect(self.on_user_response)
            self.complete_self(result)
            # END FINALIZATION and MEMORIZATION of the SLOT
            # #################################################################################
        else:
            # wrong response (
            self.recept_fails_counter += 1
            self.state = self.IGNORED
            self.save()
            print("IGNORED")
            #import ipdb; ipdb.set_trace()
            # TODO refactor
            # #################################################################################
            # ########## Requestioning Strategy Exploitation ##################################
            if self.slot.requestioning_strategy == "Greed":

                # Greed reAsk Strategy:
                print("Slot Unhandled (Greed reAsk Strategy). ReAsking...")
                self.user_domain.udm.DialogPlanner.sendText(self.slot.asker_fn()+ " (Greed ReAsk Strategy)")

                # print("Slot Unhandled (Passive waiting Strategy)")
            elif self.slot.requestioning_strategy == "ResumeOnIdle":
                # self.ic.reaskers_queue.append(self)
                # if self.recept_fails_counter >= 3:
                #     print("Slot Unhandled (ResumeOnIdle). ReAsking...")
                #     self.ic.userdialog.send_message_to_user(self.slot.asker_fn() + " (ResumeOnIdle ReAsk Strategy)")
                # import ipdb; ipdb.set_trace()

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

    def _clean_queue_of_tasks(self):
        # TODO move to dialog planner/ agenda?
        self.user_domain.agenda.reload()
        for each_slot_task in self.user_domain.agenda.queue_of_tasks:
            if self.slot == each_slot_task.item:
                #import ipdb;
                #ipdb.set_trace()

                self.user_domain.agenda.queue_of_tasks.remove(each_slot_task)
                self.user_domain.agenda.save()
                break
        else:
            # no tasks with that shit
            return

        self._clean_queue_of_tasks()

    def complete_self(self, result):
        """
        Implements finalization of slot process with provided result
        :param result:
        :return:
        """
        # self.result = UserSlot(self.user, self.slot, result)
        # self.result.save()
        self.reload()
        self.raw_result = result
        if self.state == self.COMPLETED:
            # already completed!
            print(self)
            import ipdb; ipdb.set_trace()
            print(self)

        self.state = self.COMPLETED

        if self.target_uri:
            # write the memory
            self.user_domain.udm.MemoryManager.put_slot_value(self.target_uri, result)

        # now we should remove question under discussion (if we are in active questioning process)
        # if self.slot in self.ic.DialogPlanner.questions_under_discussion:

        if self.slot in self.user_domain.agenda.questions_under_discussion:
            self.user_domain.agenda.questions_under_discussion.remove(self.slot)
            print("self.slot")
            print(self.slot)
            print("self.user_domain.agenda.questions_under_discussion=")
            print(self.user_domain.agenda.questions_under_discussion)
            self.user_domain.agenda.save()
            #import ipdb; ipdb.set_trace()
        if self.user_domain.agenda.urgent_slot_tasks:
            # find slot in tasks
            for each_urgent_slot_task in self.user_domain.agenda.urgent_slot_tasks:
                if self.slot == each_urgent_slot_task.item:
                    self.user_domain.agenda.urgent_slot_tasks.remove(each_urgent_slot_task)
                    self.user_domain.agenda.save()
                    break
        if self.user_domain.agenda.queue_of_tasks:
            self._clean_queue_of_tasks()

            # self.ic.DialogPlanner.questions_under_discussion.remove(self.slot)
        self.save()
        print("User response filled slot %s: %s!" % (self.slot, result))
        #if 'MUSIC' in result:
        ##
        ##     import traceback
        ##     for line in traceback.format_stack():
        ##         print(line.strip())
        #    print(result)
        #    # UserSlotProcess.objects(user_domain=self.user_domain, slot=self.slot)
        #    import ipdb;
        #    ipdb.set_trace()
        #    print(result)
        #import ipdb; ipdb.set_trace()

        self.slot_filled_signal.send(signal_type="SlotFilledSignal", sender=self, slot=self.slot,
                                     user_slot_process=self, results=result)

    def fast_evaluation_process_attempt(self):
        """
        Attempt to evaluate slot without Interacting with User via ActiveQuestioning process
        :return:
        """
        # import ipdb; ipdb.set_trace()
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

                is_recepted, results = slot_spec_obj.prehistory_recept(self.user_domain.udm.userdialog)
                if is_recepted:
                    print("Recepted Slot from Prehistory!")
                    print(results)
                    # if self.target_uri:
                    # write the memory
                    self.user_domain.udm.MemoryManager.put_slot_value(self.target_uri, results)

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
        return "UserDomain: %s, slot: %s, state: %s" % (self.user_domain, self.slot_codename, self.state)