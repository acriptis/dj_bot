from components.dialog_management.base_dialog_planner import BaseDialogPlanner
from components.dialog_management.agenda import Agenda
from components.dialog_management.tasks import InteractionTask, SlotTask
from components.user_processes.user_interaction_process import UserInteractionProcess


class DialogPlanner():
    """
    Manager for Dialog Session planning. It allows to enqueue Interactions, SlotProcesses for future execution and
    subscribing for results of the completed Processes
    """

    # tasks queue collector
    def __init__(self, ic):
        self.ic = ic

        # list of tasks to be done in dialog
        if not self.ic.user_domain.agenda:

            self.ic.user_domain.agenda = Agenda()
            self.ic.user_domain.agenda.save()
            self.ic.user_domain.save()
        self.agenda = self.ic.user_domain.agenda

        # slots asked to user but not percepted (waiting answer):
        # questions under discussion stack (the newest are on top):
        # self.questions_under_discussion = []
        # we restrict the system to have only one pending-asked question (to reduce ambiguity in recepted answers)

        # question (slot instance) asked to the user on current system step, nullifies after each user's response
        # helps to avoid double questioning
        # self.current_step_active_question = None

        # # the list of Processes which *want* to resume when Active Topic will be completed
        # # This is the list of processes that was ignored by User-counter-question-or-intent command
        # self.processes_waiting_to_resume = []

        ############################################
        # TODO Agenda loop DOCumentation

        # dictionary for callback functions which must be called after particular interactions completed
        self.callbacks_on_completion_of_interactions = {}
        # ^^ TODO delegate task management to celery?

        self.callbacks_on_completion_of_slots = {}
        # TODO delegate listeners functionality to EventProcessingBus?
        # self.callbacks_on_completion_of_interactions = {
        #     "<interaction_name>": [cb_fn1, cb_fn2...]
        # }

        # hacky storage to avoid dead callbacks (garbage Collected)
        self._callbacks_storage = []


    # SendText Operation
    def sendText(self, text_template):
        """
        Question:

        It seems better to push SendText operations into queue of the interaction (for better conflict resolution)
        but we need lightweight result now, so do the easiest implementation which sends text directly

        :param text_template:
        :return:
        """
        # self.ic.userdialog.send_message_to_user(text_template)
        self.ic.user_domain.pending_utterances.append(text_template)
        self.ic.user_domain.save()

    # #### SLOT PROCESS ###############################################################################################
    def remind_retrospect_or_retrieve_slot(self, slot_spec_name, target_uri=None, callback=None,
                                           priority=10):
        """
        Method to push task about slot evaluation into agenda.

        Interface method for domain interactions which encapsulates slots management as
        knowledge-agnostic interface. Callers of method don't know if the value exist already
        or must be retrieved through interactive process.

        Algorithm:
            The system requests slot from memory,
                if memory check fails
                    the system tries to apply retrospection process
                        (anlyse dialog prehistory to extract slot value from user's messages),
                    if retrospection fails
                        the system launches ActiveQuestioningProcess or default value retrieval

        Args:
            slot_spec_name: Slot name to be evaluated
            target_uri: URI for writing the result value
            callback: function to be called when the value will be retrieved
            priority:

        Returns:
        
        """
        slot_spec_obj = self.ic.sm.get_or_create_instance_by_slotname(slot_spec_name)

        if not target_uri:
            # means uri is slot name for singleton slots
            target_uri = slot_spec_obj.get_name()

        usp, created = self.ic.uspm.get_or_create_user_slot_process(slot_spec_obj, target_uri=target_uri)
        # usp.ic = self.ic
        is_recepted, result = usp.fast_evaluation_process_attempt()
        if is_recepted:
            if callback:
                # announce callback
                # TODO CONSIDER
                # what if this is not first evaluation attempt of the slot and
                # the slot process is already in the agenda?

                # it may cause situation when some processes subscribed for the slot when prehistory had no answer,
                # but during the waiting in the agenda chat went on and user has replied with providing the answer for
                # a slot that is not actively asked yet.
                # if we call only the latest callback, then we must gurantee that older listeners that are waiting since
                # previous requests are not misinformed? (Very unlikely case)
                callback(result)
        else:
            # can not retrieve slot withpout questioning

            # #########################################################################
            # ###### User Slot Retrieval Process #####################################
            # enqueue Active Questioning Process
            self.plan_process_retrieve_slot_value_with_slot_spec_instance(slot_spec_obj,
                                                                          priority=priority,
                                                                          callback_fn=callback,
                                                                          target_uri=target_uri,
                                                                          duplicatable=False)

    def plan_process_retrieve_slot_value_by_slot_name(self, slot_name, priority=10,
                                                      callback_fn=None,
                                                      duplicatable=False, target_uri=None):
        """
        Given a string of slot name it runs the process of slot-filling with ActiveQuestioning
        :param slot_name:
        :param priority:
        :param callback_fn:
        :param duplicatable:
        :return:
        """
        slot_spec_obj = self.ic.sm.get_or_create_instance_by_slotname(slot_name)
        self.plan_process_retrieve_slot_value_with_slot_spec_instance(slot_spec_obj,
                                                                      priority=priority,
                                                                      callback_fn=callback_fn,
                                                                      target_uri=target_uri,
                                                                      duplicatable=duplicatable)

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

        self.agenda.push_slot_task_by_attrs(slot_spec_obj, priority, callback_fn,
                                            duplicatable=duplicatable, target_uri=target_uri)

        # # TODO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # if slot_spec_obj.name not in self.callbacks_on_completion_of_interactions:
        #     self.callbacks_on_completion_of_interactions[interaction_obj.name] = []
        #
        # if callback_fn:
        #     self.callbacks_on_completion_of_interactions[interaction_obj.name].append(callback_fn)

    def _evaluate_slot_task(self, slot_spec_obj, priority=10, callback_fns=None,
                            duplicatable=False, target_uri=None):
        """
        Slot Task Process

        Given a slot obj it runs the process of slot-filling
        initializes process of retrieving the slot value for the user.

        If not sure wether slot already retrieved or not it better to use:
            self.ic.retrospect_or_retrieve_slot(slot_spec, target_uri, callback)

        Activate user interaction with the highest priority if there is no more active?

        Args:
            slot_spec_obj:
            priority: higher value - higher priority of execution
            callback_fns: function which must be called when slot process complete
            duplicatable: bool if, True then slot is retrieved again even if it already exists
                in memory. If False then slot will not be retrieved if it was grasped before.
            target_uri: str of URI where slot value should be written to, if None then default uri
                is a name of the slot

        Returns: None

         or better to return:
            ?Promise/Deferred/Contract for Future result?

        """
        #usp = self.ic.uspm.find_user_slot_process(slot_spec_obj)
        # import ipdb; ipdb.set_trace()
        usp, created = self.ic.uspm.get_or_create_user_slot_process(slot_spec_obj, target_uri=target_uri)
        if not usp:
            import ipdb;
            ipdb.set_trace()
            raise Exception("Why there is no USP for slot: %s" % slot_spec_obj)

        # assert hasattr(usp, 'ic')
        is_recepted, result = usp.fast_evaluation_process_attempt()
        if is_recepted:
            # announce listeners
            if callback_fns:
                # import ipdb;ipdb.set_trace()
                for each_cb_fn in callback_fns:
                    try:
                        each_cb_fn(sender=self, user_slot_process=usp, results=result)
                    except Exception as e:
                        print(e)
                        import ipdb; ipdb.set_trace()
                        print(e)
            return
        else:
            # not recepted
            print("Slot is not recepted from prehistory")
        self._force_start_slot_value_retrieval_process(slot_spec_obj, priority=priority,
                                                       callback_fns=callback_fns,
                                                       target_uri=target_uri)

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
        # RUN SLOT RETRIEVAL PROCESS
        print("Actually starting slot Active Process!")
        # import ipdb; ipdb.set_trace()

        usp, created = self.ic.uspm.get_or_create_user_slot_process(curr_slot_spec_obj, target_uri=target_uri)
        # if not created:
        #     # raise Exception("found existing user slot process, while expecting creation of new one!")
        #     import ipdb; ipdb.set_trace()
        if created:
            # raise Exception("found existing user slot process, while expecting creation of new one!")
            import ipdb;
            ipdb.set_trace()

        if target_uri and usp.target_uri != target_uri:
            usp.target_uri = target_uri

        if callback_fns:
            # hack:
            self._callbacks_storage.append(callback_fns)
            # connect signals
            # import ipdb; ipdb.set_trace()
            for each_cb_fn in callback_fns:
                # usp.slot_filled_signal.connect(each_cb_fn, weak=False)
                usp.slot_filled_signal_pattern.connect(each_cb_fn, weak=False)

            # TODO how to add support of persistent routes for runtime objects?
            # usp.slot_filled_signal.connect(self._slot_process_fin, weak=False)

        usp.start(self.ic)

    def _slot_process_fin(self, *args, **kwargs):
        """
        Called when slot is finished filling we can announce listeners for this
        :param args:
        :param kwargs:
        :return:
        """
        if 'user_slot_process' in kwargs:
            usp = kwargs['user_slot_process']
            print("SLOT PROCESS (%s) FINISHED" % usp)
        else:
            import ipdb;
            ipdb.set_trace()
            print("UNRECOGNIZED SLOT PROCESS FINISHED")
        # TODO do we need to do something here?

        # We may write the slot results into persistent memory

    # #### END SLOT PROCESS ##########################################################################################

    # Interactions Management ########################################################################################
    def enqueue_interaction(self, interaction_obj, priority=10, callback_fn=None):
        """
        Puts interaction object into Agenda of User

        Args:
            interaction_obj: Interaction
            priority: int: priority of interaction in case of multiple pending interactions in Agenda
            callback_fn: function of callback when result will be ready

        Returns:

        """
        print("DialogPlanner.Enqueue interaction: %s" % interaction_obj)
        # self.queue.append((interaction_obj, priority))

        self.agenda.push_interaction_task_by_attrs(interaction_obj, priority, callback_fn)
        if interaction_obj.name not in self.callbacks_on_completion_of_interactions:
            self.callbacks_on_completion_of_interactions[interaction_obj.name] = []

        if callback_fn:
            self.callbacks_on_completion_of_interactions[interaction_obj.name].append(callback_fn)

    def enqueue_interaction_by_name(self, interaction_name, priority=10, callback_fn=None):
        """
        Given interaction name pushes it into plan of execution
        :param interaction_name:
        :param priority:
        :return:
        """
        # TODO make interactions registry!!!!!
        # resolve interaction obj from name:
        interaction_obj = self.ic.im.get_or_create_instance_by_name(interaction_name)
        self.enqueue_interaction(interaction_obj, priority=priority, callback_fn=callback_fn)

    # #############################################################################################
    # USER INTERACTION management:

    # def initialize_user_interaction_proc(self, interaction_obj):
    #     """
    #     Interface method for starting User Interaction
    #
    #     called by Interaction usually when start method is launched?
    #     :param interaction_obj:
    #     :return:
    #     """
    #     # TODO move to ?
    #     uip, _ = UserInteraction.objects.get_or_create(interaction=interaction_obj, userdialog=self.ic.userdialog)
    #     return uip

    def complete_user_interaction_proc(self, interaction_obj, exit_gate):
        """
        Completes UserInteraction process given Interaction obj
            changes state to Completed
            emits Signal of Interaction completion
        :param interaction_obj:
        :param exit_gate:
        :return:
        """
        print("DialogPlanner.Completing_interaction: %s/%s" % (interaction_obj, exit_gate))

        interaction_obj.save()
        ui, _ = UserInteractionProcess.get_or_create(interaction=interaction_obj,
                                                     user_domain=self.ic.user_domain)

        if ui.state != UserInteractionProcess.COMPLETED:
            ui.state = UserInteractionProcess.COMPLETED
            ui.save()
            # interaction_obj.EXIT_GATES_SIGNALS[exit_gate].send(sender=self,
            #                                                    userdialog=self.ic.userdialog)
            # import ipdb; ipdb.set_trace()

            ui.EXIT_GATES_SIGNALS[exit_gate].send(sender=self,
                                                  userdialog=self.ic.userdialog)

        else:
            print(
                'DialogPlanner.complete_interaction: Interaction %s already completed!' % interaction_obj)
            print("Investigate me!")

        # Callbacks routing:
        # now cal callbacks:
        print("self.callbacks_on_completion_of_interactions")
        print(self.callbacks_on_completion_of_interactions)

        if interaction_obj.name in self.callbacks_on_completion_of_interactions and len(
                self.callbacks_on_completion_of_interactions[interaction_obj.name]) > 0:
            # run callbacks:
            for each_cb_fn in self.callbacks_on_completion_of_interactions[interaction_obj.name]:
                # import ipdb; ipdb.set_trace()

                each_cb_fn(userinteraction=ui)
        ##############################################################################

        # finally we need to drop interaction from queue (if it exists there)
        # if interaction_obj
        task = self.agenda.pop_by_interaction_obj(interaction_obj)
        if not task:
            # import ipdb; ipdb.set_trace()

            # raise Exception("Im not in Agenda???? Why???")
            print("Im not in Agenda???? Why???")

        else:
            print("Moved completed interaction %s from queue into done_list" % task.interaction_obj)
        print("DialogPlanner.COMPLETED INTERACTION: %s/%s" % (interaction_obj, exit_gate))

    def _force_start_interaction_process(self, interaction_obj, priority=10, callback_fn=None):
        """
        Actually starts Interaction Process
        :param interaction_obj:
        :param priority:
        :param callback_fn:
        :return:
        """
        # ASIS instant launching of interaction:
        # TODO: clarify best practice of how to initilize interactions
        #   when should we initialize it from class spec?
        #   when should we retrieve prepared instance from registry
        print("Next Task is interaction_obj: %s" % interaction_obj)
        # interaction_obj.save()
        ui, _ = UserInteractionProcess.get_or_create(user_domain=self.ic.user_domain,
                                                     interaction=interaction_obj)

        interaction_obj.start(user_domain=self.ic.user_domain)

    # END USER Interactions Management ########################################################################################
    # END Interactions Management ########################################################################################

    # General Management

    def process_agenda(self):
        """Agenda processing

        Recursive function for launching Dialog Tasks until condition for "end of dialog step"
        occurs.

        It exists decisioning loop in any of following cases:
        1. There is current_step_active_question specified
        2. There is no more tasks in Agenda

        Returns: None when all tasks for current step are done

        """
        # import ipdb; ipdb.set_trace()

        # update data model:
        self.ic.user_domain.reload()
        self.agenda.reload()

        print("Processing agenda")

        if self.agenda.current_step_active_question:
            # we asked something at this step. Don't overload the User, wait his response
            return

        print(f"process_agenda: urgent_slot_tasks: {self.agenda.urgent_slot_tasks}")
        print(
            f"process_agenda: questions_under_discussion: {self.agenda.questions_under_discussion}")
        print(f"process_agenda: pending tasks: {self.agenda.queue_of_tasks}")
        if self.agenda.urgent_slot_tasks:
            print(f"process_agenda: Have urgent_slot_tasks: {self.agenda.urgent_slot_tasks}")
            # ask them first
            urgent_task_slot = self.agenda.urgent_slot_tasks.pop(0)
            self.agenda.queue_of_tasks.remove(urgent_task_slot)
            self._launch_task(urgent_task_slot)
            return

        if len(self.agenda.questions_under_discussion) > 0:
            print(f"process_agenda: Have questions_under_discussion: {self.agenda.questions_under_discussion}")
            # we have no active_question at current step, but have questions_under_discussion (Ignored Slots)
            #   re-ask a question in ReAsk queue
            slot_to_ask = self.agenda.questions_under_discussion[0]
            # import ipdb; ipdb.set_trace()

            user_slot = self.ic.uspm.find_user_slot_process(slot_to_ask)
            user_slot.reasking_process()
            return

        if len(self.agenda.queue_of_tasks) == 0:
            return
        else:
            print(f"process_agenda: Have pending tasks: {self.agenda.queue_of_tasks}")
            launched_task = self.launch_next_task()
            if launched_task:
                # launched something then we need to re-run processing loop
                self.process_agenda()
                return
            else:
                # Exception?
                import ipdb;
                ipdb.set_trace()
                print("Investigate me!")

    def launch_next_task(self):
        """Starts the most prioritized item (Interaction or Slot) from queue

        Returns: Task launched if something launched, None if nothing to launch
        """

        if len(self.agenda.queue_of_tasks) > 0:
            next_task = self.agenda.pop_the_highest_priority_task()
            # import ipdb; ipdb.set_trace()
            self._launch_task(next_task)
            return next_task
        else:
            return None

    def _launch_task(self, task):
        """Given a task object starts it (Slot Process or Interaction Process)

        Args:
            task: BaseTask instance (InteractionTask or SlotTask)

        Returns:

        """
        if isinstance(task, InteractionTask):
            interaction_obj = task.interaction_obj
            self._force_start_interaction_process(interaction_obj)
        elif isinstance(task, SlotTask):
            slot_obj = task.item
            # slots must be carefully started! with check if they already completed,
            # or in process so we neeed to call
            # import ipdb; ipdb.set_trace()
            # lets investigate the case
            self._evaluate_slot_task(slot_obj, task.priority, task.callback_fns, task.kwargs)
        return
