from interactions.models import UserSlotProcess, UserInteraction
from bank_interactions.models import IntentRetrievalInteraction, DesiredCurrencyInteraction, BusinessOfferingInteraction


class DialogPlanner():
    # tasks queue collector
    def __init__(self, ic):
        self.ic = ic
        self.queue = []


        # storage for listeners

        self.listeners = {
            # example
            'slot_obj': ['listeners_fn1', 'listeners_fn2']
        }
        # TODO delegate listeners funstionality to EventProcessingBus?

    # #### SLOT PROCESS ###############################################################################################
    def plan_process_retrieve_slot_value(self, slot_specification_cls, priority=10, callback_fn=None):
        """
        Given a slot specification initializes process of retrieving
        the slot value for the user.

        Activate user interaction with the highest priority if there is no more active?

        :param slot_specification_cls:
        :param priority: higher value - higher priority of execution
        :param callback_fn: function which must be called when slot process complete
        :return: UserSlotProcess

         or better to return:
            ?Promise/Deferred/Contract for Future result?
        """
        # self.queue.append(slot_specification_cls)
        # print("DialogPlanner: Implement Me")

        # TODO implement TASK management with priority accounting and analysis of current active interactions
        # TODO make possible to trigger starts of interactions after finishing other planned (or not planned?)
        # TODO interactions

        # ASIS instant launching of interaction:
        curr_slot_spec = slot_specification_cls()

        # ProcessPipe([])

        self.usp = UserSlotProcess.initialize(self.ic.user, curr_slot_spec)
        self.usp.start(self.ic)
        self.usp.save()
        if callback_fn:
            self.usp.slot_filled_signal.connect(callback_fn)
            self.usp.slot_filled_signal.connect(self._slot_process_fin)
        # or do we need to call _slot_process_fin?
        return self.usp

    def _slot_process_fin(self, *args, **kwargs):
        """
        Called when slot is finished filling we can announce listeners for this
        :param args:
        :param kwargs:
        :return:
        """
        print("sklot process fin")
        #TODO do we need to do something here?

        pass

    # #### END SLOT PROCESS ##########################################################################################

    # Interactions Management ########################################################################################
    def enqueue_interaction(self, interaction_obj, priority=10, callback_fn=None):
        print("DialogPlanner.Enqueue interaction: %s" % interaction_obj)
        self.queue.append(interaction_obj)

    def enqueue_interaction_by_name(self, interaction_name, priority=10, callback_fn=None):
        """
        Given interaction name pushes it into plan of execution
        :param interaction_name:
        :param priority:
        :return:
        """
        # TODO make interactions registry!!!!!
        # resolve interaction obj from name:
        interactions_index = {
            "IntentRetrievalInteraction": IntentRetrievalInteraction,
            "DesiredCurrencyInteraction": DesiredCurrencyInteraction,
            "BusinessOfferingInteraction": BusinessOfferingInteraction,
        }
        if interaction_name in interactions_index.keys():
            self.enqueue_interaction(interactions_index[interaction_name])

    # #############################################################################################
    # USER INTERACTION management:
    def initialize_user_interaction_proc(self, interaction_obj):
        """
        Interface method for starting User Interaction
        :param interaction_obj: 
        :return: 
        """
        usp = UserInteraction.objects.get_or_create(interaction=interaction_obj, userdialog=self.ic.userdialog)
        return usp
    
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
        # hack if interaction is not saved yet
        interaction_obj.save()
        # TODO if someoine wants to be announced about interaction completion?
        ui, _ = UserInteraction.objects.get_or_create(interaction=interaction_obj, userdialog=self.ic.userdialog)
        if ui.state != UserInteraction.COMPLETED:
            ui.state = UserInteraction.COMPLETED
            ui.save()
            # interaction_obj.exit_gate_signal.send(sender=self, userdialog=self.ic.userdialog)
            interaction_obj.EXIT_GATES_SIGNALS[exit_gate].send(sender=self, userdialog=self.ic.userdialog)
        else:
            print('DialogPlanner.complete_interaction: Interaction %s already completed!' % interaction_obj)
            import ipdb; ipdb.set_trace()
            print("Investigate me!")

        # self.queue.append(intreaction_obj)
        # import ipdb; ipdb.set_trace()

        print("DialogPlanner.Complete_interaction: %s/%s" % (interaction_obj, exit_gate))

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
        next_element = self.queue[0]

        self.queue = self.queue[1:]

        # ASIS instant launching of interaction:
        interaction_obj = next_element.initialize(self.ic)
        ui, _ = UserInteraction.objects.get_or_create(interaction=interaction_obj, userdialog=self.ic.userdialog)
        # ui.state = UserInteraction.COMPLETED
        # ui.save()
        # ProcessPipe([])
        #
        # self.usp.start(self.ic)
        # self.usp.save()
        # if callback_fn:
        #     self.usp.slot_filled_signal.connect(callback_fn)
        # or do we need to call _slot_process_fin?
        return