from interactions.models import UserSlotProcess, UserInteraction, UserSlot
from bank_interactions.models import IntentRetrievalInteraction, DesiredCurrencyInteraction, \
    BusinessOfferingInteraction, PrivateInfoFormInteraction, DocumentsListSupplyInteraction


# class Task():
#     def __init__(self, task_name, task_obj, task_args, completion_callbacks):
#         self.task_name, task_obj, task_args, completion_callbacks
#         task_name, task_obj, task_args, completion_callbacks
#
# class SlotTask():
#     """
#     Task to complete slot and call callback
#
#     Each slot task is always check if slot already was retrieved in this case it just sends result to callbacks
#     Otherwise starts userslot retrieval process
#     Process may be active... in this case we need to wait the completion of slot and then trigger callback
#     """
#     def __init__(self, slot, callback_fn):
#         self.slot = slot
#         self.callback_fn = callback_fn
#

class InteractionTask():
    def __init__(self, interaction_obj, priority, callback_fn):
        self.interaction_obj=interaction_obj
        self.priority=priority
        self.callback_fn=callback_fn

class Agenda():
    """
    class keeping all tasks of the system
    """
    def __init__(self):

        self.queue_of_tasks = []


        self.interactions_in_queue = {}

    def is_interaction_in_queue(self, interaction_obj):
        pass


    def find_task_by_interaction(self, interaction_obj):
        """
        returns first match
        :param interaction_obj:
        :return:
        """
        for each_task in self.queue_of_tasks:
            if interaction_obj == each_task.interaction_obj:
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

    def push_task_by_attrs(self, interaction_obj, priority, callback_fn):
        itask = InteractionTask(interaction_obj, priority, callback_fn)
        self.queue_of_tasks.append(itask)
        return itask

class DialogPlanner():
    # tasks queue collector
    def __init__(self, ic):
        self.ic = ic
        self.agenda = Agenda()
        # here we put Interactions to be done in future
        # self.queue = []

        # queue is a list of tuples (Interaction, priority)
        # separate queue for slots
        self.slots_queue = []
        # slots queue is higher priority than Interactions queue?

        # here we put decisions which are processed or started processing
        self.done_or_doing = []

        # dictionary for callbacks which must be called after particular interactions will be completed
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

    def plan_process_retrieve_slot_value(self, slot_specification_cls, priority=10, callback_fn=None, duplicatable=False):
        """
        Given a slot specification initializes process of retrieving
        the slot value for the user.

        Activate user interaction with the highest priority if there is no more active?

        :param slot_specification_cls:
        :param priority: higher value - higher priority of execution
        :param callback_fn: function which must be called when slot process complete
        :param duplicatable: bool if, True then slot is retrieved again even if it already exists in memory.
            If False then slot will not be retrieved if it was grasped before
        :return: UserSlotProcess

         or better to return:
            ?Promise/Deferred/Contract for Future result?

        """
        print("DialogPlanner: plan_process_retrieve_slot_value: %s" % slot_specification_cls.name)

        # TODO implement TASK management with priority accounting and analysis of current active interactions
        # TODO make possible to trigger starts of interactions after finishing other planned (or not planned?)
        # TODO interactions


        curr_slot_obj = self.ic.sm.get_or_create_instance_by_class(slot_specification_cls)

        if not duplicatable:
            # check existence of ready value:
            results = self.ic.MemoryManager.get_slot_value_quite(curr_slot_obj.get_name())
            # import ipdb; ipdb.set_trace()

            if not results:

                # RUN RETRIEVAL PROCESS (or Attach callback to existing process)
                # check if process exists:
                usp = self.ic.uspm.find_user_slot_process(curr_slot_obj)
                if usp:
                    # exists
                    # assert is not completed
                    if usp.state == UserSlotProcess.COMPLETED:
                        # investigate
                        raise Exception("Result is not written but process is completed!")
                    else:
                        usp.slot_filled_signal.connect(callback_fn)

                else:
                    # if usp is None
                    # no process exist we must create a new one:
                    self._force_plan_process_retrieve_slot_value(curr_slot_obj, priority=priority,
                                                             callback_fn=callback_fn)
            else:
                # RETRIEVE CACHED RESULTS! (No need to ReRun process)
                # means we can call callbacks instantly
                # TODO refactor below:
                if callback_fn:
                    # import ipdb; ipdb.set_trace()
                    # emulate slot process:
                    usps = self.ic.uspm.find_user_slot_process(curr_slot_obj)
                    # usps= UserSlotProcess.objects.filter(user=self.ic.user, slot_codename=curr_slot_obj.name)
                    if usps:
                        # get first
                        usp =usps[0]
                        usp.result = UserSlot(user=self.ic.user,slot=curr_slot_obj,value=results)

                    else:
                        # import ipdb; ipdb.set_trace()
                        print("No UserSlotProcess, while result exists!")
                        raise Exception("Result exist and UserSlotProcess no???")
                        # usp = UserSlotProcess(user=self.ic.user, slot_codename=curr_slot_obj.name)
                        #
                        # usp.result = UserSlot(user=self.ic.user, slot=curr_slot_obj, value=results)

                    callback_fn(sender=self, user_slot_process=usp)
                    return
                else:
                    return
        else:
            raise Exception("Duplicatable Slots are not supported yet!")

    def _force_plan_process_retrieve_slot_value(self, curr_slot_spec_obj, priority=10, callback_fn=None):
        """
        Method which actually starts slot process in system and attaches callback on its completion

        :param curr_slot_spec_obj:
        :param priority:
        :param callback_fn:
        :return:
        """
        # self.ic.uspm.goalize_user_slot_process
        # RUN RETRIEVAL PROCESS
        # self.usp = UserSlotProcess.initialize(self.ic.user, curr_slot_spec_obj)
        # import ipdb; ipdb.set_trace()

        usp, created = self.ic.uspm.get_or_create_user_slot_process(curr_slot_spec_obj)
        if not created:
            raise Exception("found existing user slot process, while expecting creation of new one!")

        if callback_fn:
            # hack:
            self._callbacks_storage.append(callback_fn)
            # connect signals
            usp.slot_filled_signal.connect(callback_fn)
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

        self.agenda.push_task_by_attrs(interaction_obj, priority, callback_fn)
        if interaction_obj.name not in self.callbacks_on_completion_of_interactions:
            self.callbacks_on_completion_of_interactions[interaction_obj.name] = []

        # import ipdb; ipdb.set_trace()

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
        interaction_obj= self.ic.im.get_or_create_instance_by_classname(interaction_name)
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

    # END USER Interactions Management ########################################################################################
    # END Interactions Management ########################################################################################

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

    # General Management
    def launch_next_task(self):
        """
        Starts the most prioritized item (Interaction or Slot) from queue
        :return:
        """
        # import ipdb; ipdb.set_trace()

        next_task = self.agenda.pop_the_highest_priority_task()

        interaction_obj = next_task.interaction_obj

        self.done_or_doing.append(interaction_obj)
        # import ipdb; ipdb.set_trace()

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
        #
        # if type(type(next_element)) == type
        return