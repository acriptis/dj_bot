class BaseDialogPlanner():
    # tasks queue collector
    def __init__(self, ic):
        raise Exception("NotImplemented")

    # #### SLOT PROCESS ###############################################################################################
    def remind_retrospect_or_retrieve_slot(self, slot_spec_name, target_uri=None, callback=None,
                                           priority=10):

        raise Exception("NotImplemented")

    def plan_process_retrieve_slot_value_by_slot_name(self, slot_name, priority=10,
                                                      callback_fn=None,
                                                      duplicatable=False):
        """
        Given a string of slot name it runs the process of slot-filling with ActiveQuestioning
        :param slot_name:
        :param priority:
        :param callback_fn:
        :param duplicatable:
        :return:
        """
        raise Exception("NotImplemented")

    def plan_process_retrieve_slot_value_with_slot_spec_instance(self, slot_spec_obj, priority=10,
                                                                 callback_fn=None,
                                                                 duplicatable=False,
                                                                 target_uri=None):
        """
        Infrastructure method for appending slot process to Agenda


        Given a slot obj it runs the process of slot-filling
        initializes process of retrieving the slot value for the user.

        If not sure wether slot already retrieved or not it better to use:
            self.ic.retrospect_or_retrieve_slot(slot_spec, target_uri, callback)

        Activate user interaction with the highest priority if there is no more active?

        :param slot_spec_obj:
        :param priority: higher value - higher priority of execution
        :param callback_fn: function which must be called when slot process complete

        :param target_uri: str of URI where slot value should be written to, if None then default uri is a name of the slot

        :param duplicatable: bool if, True then slot is retrieved again even if it already exists in memory.
            If False then slot will not be retrieved if it was grasped before
        :return: UserSlotProcess

         or better to return:
            ?Promise/Deferred/Contract for Future result?

        """
        raise Exception("NotImplemented")

    def _evaluate_slot_task(self, slot_spec_obj, priority=10, callback_fns=None,
                            duplicatable=False, target_uri=None):
        """
        Slot Task Process

        Given a slot obj it runs the process of slot-filling
        initializes process of retrieving the slot value for the user.

        If not sure wether slot already retrieved or not it better to use:
            self.ic.retrospect_or_retrieve_slot(slot_spec, target_uri, callback)

        Activate user interaction with the highest priority if there is no more active?

        :param slot_spec_obj:
        :param priority: higher value - higher priority of execution
        :param callback_fns: function which must be called when slot process complete

        :param target_uri: str of URI where slot value should be written to, if None then default uri is a name of the slot

        :param duplicatable: bool if, True then slot is retrieved again even if it already exists in memory.
            If False then slot will not be retrieved if it was grasped before
        :return: None

         or better to return:
            ?Promise/Deferred/Contract for Future result?

        """
        raise Exception("NotImplemented")

    def _force_start_slot_value_retrieval_process(self, curr_slot_spec_obj, target_uri, priority=10,
                                                  callback_fns=None):
        """
        Method which actually starts slot process in system and attaches callback on its completion
        (1.2.3.1.DialogUserSlotRetrievalProcess or 1.2.SlotFillingProcess?)

        :param curr_slot_spec_obj:
        :param priority:
        :param callback_fns:
        :return:
        """
        raise Exception("NotImplemented")

    def _slot_process_fin(self, *args, **kwargs):
        """
        Called when slot is finished filling we can announce listeners for this
        :param args:
        :param kwargs:
        :return:
        """
        raise Exception("NotImplemented")
    # #### END SLOT PROCESS ##########################################################################################

    # Interactions Management ########################################################################################
    def enqueue_interaction(self, interaction_obj, priority=10, callback_fn=None):
        raise Exception("NotImplemented")

    def enqueue_interaction_by_name(self, interaction_name, priority=10, callback_fn=None):
        """
        Given interaction name pushes it into plan of execution
        :param interaction_name:
        :param priority:
        :return:
        """
        raise Exception("NotImplemented")
    # #############################################################################################
    # USER INTERACTION management:
    def complete_user_interaction_proc(self, interaction_obj, exit_gate):
        """
        Completes UserInteraction process given Interaction obj
            changes state to Completed
            emits Signal of Interaction completion
        :param interaction_obj:
        :param exit_gate:
        :return:
        """
        raise Exception("NotImplemented")

    def _force_start_interaction_process(self, interaction_obj, priority=10, callback_fn=None):
        """
        Actually starts Interaction Process
        :param interaction_obj:
        :param priority:
        :param callback_fn:
        :return:
        """
        raise Exception("NotImplemented")

    # END USER Interactions Management ########################################################################################
    # END Interactions Management ########################################################################################

    # General Management

    def process_agenda(self):
        """
        Refactored Agenda processing version

        it exists decisioning loop in any of following cases:
        1. There is exist a question on discussion
        2. There is no more tasks in Agenda

        :return: None when all tasks for current step are done
        """
        raise Exception("NotImplemented")

    def launch_next_task(self):
        """
        Starts the most prioritized item (Interaction or Slot) from queue
        :return: Task launched if something launched, None if nothing to launch
        """
        if len(self.agenda.queue_of_tasks) > 0:
            next_task = self.agenda.pop_the_highest_priority_task()
            # import ipdb; ipdb.set_trace()
            self._launch_task(next_task)
            return next_task
        else:
            return None

    def _launch_task(self, task):
        """
        Givewn a task object starts it (Slot Process or Interaction Process)
        :param task:
        :return:
        """
        raise Exception("NotImplemented")

    # SendText Operation
    def sendText(self, text_template):
        """
        Question:

        It seems better to push SendText operations into queue of the interaction (for better conflict resolution)
        but we need lightweight result now, so do the easiest implementation which sends text directly

        :param text_template:
        :return:
        """
        raise Exception("NotImplemented")
