# -*- coding: utf-8 -*-
from mongoengine import *
from components.dialog_management.tasks import InteractionTask, SlotTask


class Agenda(Document):
    """
    Class for storing the plan of future processing tasks
    """
    # tasks queue holding entities (Tasks with Slots and Interactions) which planned to be processed
    queue_of_tasks = ListField(GenericReferenceField(), default=[])

    # list of urgent tasks, they must be started before reaskings:
    urgent_slot_tasks = ListField(GenericReferenceField(), default=[])

    # slots asked to user but not percepted (waiting answer):
    # questions under discussion stack (the newest are on top):
    questions_under_discussion = ListField(GenericReferenceField(), required=False)
    # ^ each object in list is a slot object
    # TODO they are already must have a user slot process should we refactor?

    # We restrict the system to have only one pending-asked question (to reduce ambiguity in
    # recepted answers).
    # Question (slot instance) asked to the user on current system step is nullified after
    # each user's response (on each step "start"). The attribute helps to avoid double questioning.
    current_step_active_question = GenericReferenceField(required=False, default=None)

    def find_task_by_interaction(self, interaction_obj):
        """
        returns first match
        :param interaction_obj:
        :return:
        """
        for each_task in self.queue_of_tasks:
            # TODO improve code to avoid type checks?
            if isinstance(each_task,
                          InteractionTask) and interaction_obj == each_task.interaction_obj:
                return each_task

    def find_the_highest_priority(self):
        """
        :return: Task with the highest priority
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
        self.save()
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
        priority_numerical = self._priority_normalizer(priority)

        # import ipdb; ipdb.set_trace()
        # TODO fix code duplication in Interactions and slots
        if callback_fn:
            # Callback to Reflex conversion
            # here we need to make resolving of callback function into Reflex
            from components.signal_pattern_reflex.reflex import Reflex
            reflex = Reflex.receiver_fn_into_reflex(callback_fn)
            # reflex = self._callback_to_reflex_resolver(callback_fn)
            # s_task = SlotTask(item=slot_obj, priority=priority_numerical, callback_fns=[reflex], kwargs=kwargs)
            itask = InteractionTask(item=interaction_obj, priority=priority_numerical, callback_fns=[reflex])
        else:
            # s_task = SlotTask(item=slot_obj, priority=priority_numerical, callback_fns=[], kwargs=kwargs)
            itask = InteractionTask(item=interaction_obj, priority=priority_numerical, callback_fns=[])

        itask.save()
        self.queue_of_tasks.append(itask)
        # import ipdb; ipdb.set_trace()

        self.save()
        return itask

    def push_slot_task_by_attrs(self, slot_obj, priority, callback_fn, **kwargs):
        priority_numerical = self._priority_normalizer(priority)
        # import ipdb; ipdb.set_trace()
        # TODO fix code duplication in Interactions and slots
        if callback_fn:
            # Callback to Reflex conversion
            # here we need to make resolving of callback function into Reflex
            from components.signal_pattern_reflex.reflex import Reflex
            reflex = Reflex.receiver_fn_into_reflex(callback_fn)
            # reflex = self._callback_to_reflex_resolver(callback_fn)
            s_task = SlotTask(item=slot_obj, priority=priority_numerical, callback_fns=[reflex], kwargs=kwargs)
        else:
            s_task = SlotTask(item=slot_obj, priority=priority_numerical, callback_fns=[], kwargs=kwargs)
        s_task.save()
        #s_task = SlotTask(slot_obj, priority_numerical, callback_fn)
        if priority == "URGENT":
            self.urgent_slot_tasks.append(s_task)
            self.queue_of_tasks.append(s_task)
        else:
            # normal queue
            self.queue_of_tasks.append(s_task)
        self.save()
        return s_task

    # def _callback_to_reflex_resolver(self, callback_fn):
    #     try:
    #         method_name = callback_fn.__name__
    #         parent_object = callback_fn.__self__
    #         from components.signal_reflex_routes.models.reflexes import ObjectMethodReflex
    #         object_method_reflex, _ = ObjectMethodReflex.get_or_create(
    #             instance_locator=parent_object,
    #             method_name=method_name)
    #
    #         return object_method_reflex
    #     except Exception as e:
    #         print(e)
    #         import ipdb; ipdb.set_trace()
    #         print(e)
    #         return None

    def _priority_normalizer(self, priority_obj):
        """Priority may be numerical or URGENT
        in case of Urgent we must set numerical priority higher than current max
        """
        if priority_obj == "URGENT":
            max_priority_task = self.find_the_highest_priority()
            # just increase it
            if max_priority_task:
                final_priority = max_priority_task.priority + 1
            else:
                # TODO remove hardcode
                final_priority = 1
        else:
            final_priority = priority_obj
        return final_priority

    def reset(self):
        """
        Cleans all data from agenda used at restart event
        Returns:

        """
        self.queue_of_tasks = []
        self.urgent_slot_tasks = []
        self.questions_under_discussion = []
        self.save()

    def __str__(self):
        return f"Agenda: \nTasks:{self.queue_of_tasks}" \
                f"\nUrgent SLots:{self.urgent_slot_tasks}" \
                f"\nQUDs:{self.questions_under_discussion}"
