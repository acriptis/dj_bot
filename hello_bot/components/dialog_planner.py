from interactions.models import UserSlotProcess, UserInteraction, UserSlot


class BaseTask():
    def __init__(self, item, priority, callback_fns):
        """

        :param item: element of task
        :param priority:
        :param callback_fns: list of callback functions or a callback function
        """
        self.item = item
        self.priority = priority
        if isinstance(callback_fns, list):
            self.callback_fns = callback_fns
        else:
            if not callback_fns:
                self.callback_fns = []
            else:
                # The most used case: if one callback is provided
                self.callback_fns = [callback_fns]

    def add_callback_fn(self, cb_fn):
        """
        Adds callback function to task (which called after task completion)
        :param cb_fn:
        :return:
        """
        if not cb_fn:
            import ipdb; ipdb.set_trace()
            print("Palundra")
        self.callback_fns.append(cb_fn)

    def __repr__(self):
        return "%s --then-> %s" % (self.item, self.callback_fns)


class InteractionTask(BaseTask):
    """
    Atomic Task in Agenda

    #TODO do abstraction refactoring for managing Slots as Tasks as well
    """
    def __init__(self, interaction_obj, priority, callback_fn):
        super().__init__(interaction_obj, priority, callback_fn)

    @property
    def interaction_obj(self):
        return self.item

    def __str__(self):
        return "%s --then-> %s" % (self.interaction_obj, self.callback_fns)

    def __repr__(self):
        return "%s --then-> %s" % (self.interaction_obj, self.callback_fns)


class SlotTask(BaseTask):
    """
    Task for slot filling in Agenda

    Task to complete slot and call callback

    Each slot task is always check if slot already was retrieved, in this case it sends result to callback
    Otherwise starts userslot retrieval process
    Process may be active... in this case we need to wait the completion of slot and then trigger callback
        (add callback to listeners pool)
    """
    def __init__(self, slot_obj, priority, callback_fn, **kwargs):
        super().__init__(slot_obj, priority, callback_fn)
        self.kwargs = kwargs


class Agenda():
    """
    Class for storing the plan of future processing tasks
    """
    # TODO make agenda user specific and persistent
    def __init__(self):

        self.queue_of_tasks = []

        self.interactions_in_queue = {}

    def find_task_by_interaction(self, interaction_obj):
        """
        returns first match
        :param interaction_obj:
        :return:
        """
        for each_task in self.queue_of_tasks:
            # TODO improve code to avoid type checks?
            if isinstance(each_task, InteractionTask) and interaction_obj == each_task.interaction_obj:
                return each_task

    def find_the_highest_priority(self):
        """

        :return: Interaction with the highest priority
        """
        max_priority_value = 0
        max_priority_task = None
        for each_task in self.queue_of_tasks:
            if each_task.priority > max_priority_value:
                max_priority_task = each_task
                max_priority_value = each_task.priority

        return max_priority_task

    def pop_the_highest_priority_task(self):
        task = self.find_the_highest_priority()
        task = self.pop_task(task)
        return task

    def pop_task(self, task):
        idx = self.queue_of_tasks.index(task)
        item = self.queue_of_tasks.pop(idx)
        return item

    def pop_by_interaction_obj(self, interaction_obj):
        """
        pops the first matched interaction from agenda
        :param interaction_obj:
        :return: popped task or none
        """
        task = self.find_task_by_interaction(interaction_obj)
        if task:
            self.pop_task(task)
            return task
        else:
            return None

    def push_interaction_task_by_attrs(self, interaction_obj, priority, callback_fn):
        itask = InteractionTask(interaction_obj, priority, callback_fn)
        self.queue_of_tasks.append(itask)
        return itask

    def push_slot_task_by_attrs(self, slot_obj, priority, callback_fn, **kwargs):
        s_task = SlotTask(slot_obj, priority, callback_fn)
        self.queue_of_tasks.append(s_task)
        return s_task


class DialogPlanner():
    """
    Manager for Dialog Session planning. It allows to enqueue Interactions, SlotProcesses for future execution and
    subscribing for results of the completed Processes
    """
    # tasks queue collector
    def __init__(self, ic):
        self.ic = ic

        # list of tasks to be done in dialog
        self.agenda = Agenda()

        # here we put Interactions to be done in future
        # self.queue = []

        # # queue is a list of tuples (Interaction, priority)
        # # separate queue for slots
        # self.slots_queue = []
        # # slots queue is higher priority than Interactions queue?

        # here we put decisions which are processed or started processing
        self.done_or_doing = []

        # slots asked to user but not percepted (waiting answer):
        # questions under discussion stack (the newest are on top):
        self.questions_under_discussion = []
        # we restrict the system to have only one pending-asked question (to reduce ambiguity in recepted answers)

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

    # #### SLOT PROCESS ###############################################################################################
    def remind_retrospect_or_retrieve_slot(self, slot_spec_name, target_uri=None, callback=None, priority=10):
        """
        Interface method for domain interactions which encapsulates slots management as knowledge-agnostic interface
        (Callers of method don't know if the value exist already or must be retrieved through interactive process).
            The system requests slot from memory,
                if memory check fails
                    the system tries to apply retrospection process
                        (anlyse dialog prehistory to extract slot value from user's initiative directive),
                    if retrospection fails
                        the system launches ActiveQuestioningProcess or default value retrieval

        :param slot_spec_name: Slot name to be evaluated
        :param target_uri:
        :return:
        """

        slot_spec_obj = self.ic.sm.get_or_create_instance_by_slotname(slot_spec_name)

        if not target_uri:
            # means uri is slot name for singleton slots
            target_uri = slot_spec_obj.get_name()

        usp, created = self.ic.uspm.get_or_create_user_slot_process(slot_spec_obj)
        usp.ic = self.ic
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

    def plan_process_retrieve_slot_value_by_slot_name(self, slot_name, priority=10, callback_fn=None,
                                         duplicatable=False):
        """
        Given a string of slot name it runs the process of slot-filling with ActiveQuestioning
        :param slot_name:
        :param priority:
        :param callback_fn:
        :param duplicatable:
        :return:
        """
        slot_spec_obj = self.ic.sm.get_or_create_instance_by_slotname(slot_name)
        self.plan_process_retrieve_slot_value_with_slot_spec_instance(slot_spec_obj, priority=priority, callback_fn=callback_fn, duplicatable=duplicatable)

    def plan_process_retrieve_slot_value_with_slot_spec_instance(self, slot_spec_obj, priority=10, callback_fn=None,
                                                      duplicatable=False, target_uri=None):
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

        self.agenda.push_slot_task_by_attrs(slot_spec_obj, priority, callback_fn, duplicatable=duplicatable, target_uri=target_uri)

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

        usp = self.ic.uspm.find_user_slot_process(slot_spec_obj)
        if not usp:
            import ipdb; ipdb.set_trace()
            raise Exception("Why there is no USP for slot: %s" % slot_spec_obj)

        assert hasattr(usp, 'ic')
        is_recepted, result = usp.fast_evaluation_process_attempt()
        if is_recepted:
            # announce listeners
            if callback_fns:
                import ipdb;ipdb.set_trace()
                for each_cb_fn in callback_fns:
                    each_cb_fn(sender=self, user_slot_process=usp, results=result)
            return
        else:
            # not recepted
            print("Slot is not recepted from prehistory")
        self._force_start_slot_value_retrieval_process(slot_spec_obj, priority=priority,
                                                       callback_fns=callback_fns, target_uri=target_uri)

    def _force_start_slot_value_retrieval_process(self, curr_slot_spec_obj, target_uri, priority=10, callback_fns=None):
        """
        Method which actually starts slot process in system and attaches callback on its completion
        (1.2.3.1.DialogUserSlotRetrievalProcess or 1.2.SlotFillingProcess?)

        :param curr_slot_spec_obj:
        :param priority:
        :param callback_fns:
        :return:
        """
        # RUN SLOT RETRIEVAL PROCESS
        usp, created = self.ic.uspm.get_or_create_user_slot_process(curr_slot_spec_obj)
        # if not created:
        #     # raise Exception("found existing user slot process, while expecting creation of new one!")
        #     import ipdb; ipdb.set_trace()
        if created:
            # raise Exception("found existing user slot process, while expecting creation of new one!")
            import ipdb; ipdb.set_trace()

        if target_uri and usp.target_uri != target_uri:
            usp.target_uri = target_uri

        if callback_fns:
            # hack:
            self._callbacks_storage.append(callback_fns)
            # connect signals
            # import ipdb; ipdb.set_trace()
            for each_cb_fn in callback_fns:
                usp.slot_filled_signal.connect(each_cb_fn)
            usp.slot_filled_signal.connect(self._slot_process_fin)

        usp.start(self.ic)

        # or do we need to call _slot_process_fin?
        # return self.usp

    def _slot_process_fin(self, *args, **kwargs):
        """
        Called when slot is finished filling we can announce listeners for this
        :param args:
        :param kwargs:
        :return:
        """
        print("SLOT PROCESS FINISHED")
        #TODO do we need to do something here?

        # We may write the slot results into persistent memory
    # #### END SLOT PROCESS ##########################################################################################

    # Interactions Management ########################################################################################
    def enqueue_interaction(self, interaction_obj, priority=10, callback_fn=None):
        print("DialogPlanner.Enqueue interaction: %s" % interaction_obj)
        # self.queue.append((interaction_obj, priority))

        self.agenda.push_interaction_task_by_attrs(interaction_obj, priority, callback_fn)
        if interaction_obj.name not in self.callbacks_on_completion_of_interactions:
            self.callbacks_on_completion_of_interactions[interaction_obj.name] = []

        if callback_fn:
            self.callbacks_on_completion_of_interactions[interaction_obj.name].append(callback_fn)

    # TODO callback_fn support!!!!!!
    def enqueue_interaction_by_name(self, interaction_name, priority=10, callback_fn=None):
        """
        Given interaction name pushes it into plan of execution
        :param interaction_name:
        :param priority:
        :return:
        """
        # TODO make interactions registry!!!!!
        # resolve interaction obj from name:
        interaction_obj= self.ic.im.get_or_create_instance_by_name(interaction_name)
        self.enqueue_interaction(interaction_obj, priority=priority, callback_fn=callback_fn)

    # #############################################################################################
    # USER INTERACTION management:

    def initialize_user_interaction_proc(self, interaction_obj):
        """
        Interface method for starting User Interaction

        called by Interaction usually when start method is launched?
        :param interaction_obj: 
        :return: 
        """
        # TODO move to ?
        uip, _ = UserInteraction.objects.get_or_create(interaction=interaction_obj, userdialog=self.ic.userdialog)
        return uip
    
    def complete_user_interaction_proc(self, interaction_obj, exit_gate):
        """
        Completes UserInteraction process given Interaction obj
            changes state to Completed
            emits Signal of Interaction completion
        :param interaction_obj:
        :param exit_gate:
        :return:
        """
        # import ipdb; ipdb.set_trace()

        print("DialogPlanner.Completing_interaction: %s/%s" % (interaction_obj, exit_gate))
        # import ipdb; ipdb.set_trace()
        # hack if interaction is not saved yet
        # interaction_obj.save()
        # TODO if someoine wants to be announced about interaction completion?
        ui, _ = UserInteraction.objects.get_or_create(interaction=interaction_obj, userdialog=self.ic.userdialog)
        if ui.state != UserInteraction.COMPLETED:
            ui.state = UserInteraction.COMPLETED
            ui.save()
            # interaction_obj.exit_gate_signal.send(sender=self, userdialog=self.ic.userdialog)
            # import ipdb; ipdb.set_trace()

            self.ic.im.get_or_create_instance_by_class(interaction_obj.__class__).EXIT_GATES_SIGNALS[exit_gate].send(sender=self, userdialog=self.ic.userdialog)
            # interaction_obj.EXIT_GATES_SIGNALS[exit_gate].send(sender=self, userdialog=self.ic.userdialog)

        else:
            print('DialogPlanner.complete_interaction: Interaction %s already completed!' % interaction_obj)
            print("Investigate me!")

        # Callbacks routing:
        # now cal callbacks:
        print("self.callbacks_on_completion_of_interactions")
        print(self.callbacks_on_completion_of_interactions)

        if interaction_obj.name in self.callbacks_on_completion_of_interactions and len(self.callbacks_on_completion_of_interactions[interaction_obj.name]) > 0:
            # run callbacks:
            for each_cb_fn in self.callbacks_on_completion_of_interactions[interaction_obj.name]:
                # import ipdb; ipdb.set_trace()

                each_cb_fn(userinteraction=ui)

        # finally we need to drop interaction from queue (if it exists there)
        # if interaction_obj
        task = self.agenda.pop_by_interaction_obj(interaction_obj)
        if not task:
            # import ipdb; ipdb.set_trace()

            # raise Exception("Im not in Agenda???? Why???")
            print("Im not in Agenda???? Why???")

        else:
            self.done_or_doing.append(task.interaction_obj)
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
        self.done_or_doing.append(interaction_obj)

        # make abstraction of all process types (Slots and Interactions)
        # TODO add support of Slot Processes ?
        # ASIS instant launching of interaction:
        # TODO: clarify best practice of how to initilize interactions
        #   when should we initialize it from class spec?
        #   when should we retrieve prepared instance from registry
        # interaction_obj = next_element.initialize(self.ic)

        print("Next Task is interaction_obj: %s" % interaction_obj)

        ui, _ = UserInteraction.objects.get_or_create(interaction=interaction_obj, userdialog=self.ic.userdialog)
        interaction_obj.start()

    # END USER Interactions Management ########################################################################################
    # END Interactions Management ########################################################################################

    # General Management
    def process_agenda(self):
        """
        Refactored Agenda processing version

        it exists decisioning loop in any of following cases:
        1. There is exist a question on discussion
        2. There is no more tasks in Agenda

        :return: None
        """

        if len(self.questions_under_discussion)>0:
            # should we check when there is a question on discussion but passive strategy avoids reasking?
            # we may drown in silent loop
            return
        if len(self.agenda.queue_of_tasks) == 0:
            return
        else:
            launched_task = self.launch_next_task()
            if launched_task:
                # launched something then we need to re-run processing loop
                self.process_agenda()
                return
            else:
                # Exception?
                import ipdb; ipdb.set_trace()
                print("Investigate me!")

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
        if isinstance(task, InteractionTask):
            interaction_obj = task.interaction_obj
            self._force_start_interaction_process(interaction_obj)
        elif isinstance(task, SlotTask):
            slot_obj= task.item
            # slots must be carefully started! with check if they already completed, or in process so we neeed to call
            # import ipdb; ipdb.set_trace()
            # lets investigate the case
            self._evaluate_slot_task(slot_obj, task.priority, task.callback_fns, task.kwargs)
        return

    # Deprecated
    def process_agenda34(self, *args, **kwargs):
        """
        If we have no response to user at present step:
            then we need to try to check if agenda has pending tasks
            if agenda has pending tasks:
                we need to launch the most important and then repeat check

        :return:
        """
        import ipdb; ipdb.set_trace()

        responses_list = self.ic.userdialog.show_latest_sys_responses()

        if not responses_list:
            # no interactions have responded to the utterance...
            print("no interactions have responded to the latest utterance...")
            # no responses from system:
            # else scenario
            ########################### Check Pending Interactions Plan ##############################################
            # Alternative else scenario:
            # check if we have queue of actions in plan
            print("self.ic.DialogPlanner.agenda.queue_of_tasks")
            print(self.ic.DialogPlanner.agenda.queue_of_tasks)
            launched = self.launch_next_task()
            if launched:
                print("Launched task")


            elif len(self.questions_under_discussion)==0 :
                # here we have two cases:
                # 1. we said him something from one interaction, but don't wait any questions,
                # although we have some tasks in plan that may have questions to discuss
                # 2. we have finished communication and don't need any questions to discuss anymore
                # For the first case we need to launch next task
                # For the second case we need nothing to do

                # and not self.scenario_completed
                # Scenario Policy is not Dialog Policy!
                # how to detect if scenario has no more questions to ask?
                # TODO remove hack:
                if self.ic.MemoryManager.get_slot_value_quite("bank_scenario.terminated") is True:
                    # hacky check that scenario is completed
                    # really we need a voting system between branches of dialog, so that real termination is happens only
                    # when all voters vote for termination, otherwise we assume that there are exist branches that are
                    # may have pending actions, but this is quite peculliar case, not applicable for this banking scenario
                    pass
                else:
                    launched = self.launch_next_task()
                    if not launched:
                        # Exceptional case
                        # investigate
                        print("investigate me")
                        import ipdb; ipdb.set_trace()
                        print("investigate me")
                pass
            else:
                # nothing to say, nothing to do...
                #TODO templatize
                self.ic.userdialog.send_message_to_user("Простите, я не знаю, что Вам ответить ;)")
        else:
            # nothing to do anymore for this step
            # if we have no active questions, but have pending we may ask them now
            if len(self.questions_under_discussion)==0:
                print("MNo questions on discussion may be we can start some interaction?")
                self.launch_next_task()
            else:
                import ipdb; ipdb.set_trace()
                print("We have questrion on discussion")
            return

    # SendText Operation
    def sendText(self, text_template):
        """
        Question:

        It seems better to push SendText operations into queue of the interaction (for better conflict resolution)
        but we need lightweight result now, so do the easiest implementation which sends text directly

        :param text_template:
        :return:
        """
        self.ic.userdialog.send_message_to_user(text_template)
