from components.dialog_management.tasks import InteractionTask, SlotTask


class Agenda():
    """
    Class for storing the plan of future processing tasks
    """

    # TODO make agenda user specific and persistent
    def __init__(self):

        self.queue_of_tasks = []

        self.interactions_in_queue = {}

        # list of urgent tasks, they must be started before reaskings:
        self.urgent_slot_tasks = []

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
        itask = InteractionTask(interaction_obj, priority_numerical, callback_fn)
        self.queue_of_tasks.append(itask)
        return itask

    def push_slot_task_by_attrs(self, slot_obj, priority, callback_fn, **kwargs):

        priority_numerical = self._priority_normalizer(priority)
        s_task = SlotTask(slot_obj, priority_numerical, callback_fn)
        if priority == "URGENT":
            self.urgent_slot_tasks.append(s_task)
            self.queue_of_tasks.append(s_task)
        else:
            # normal queue
            self.queue_of_tasks.append(s_task)
        return s_task

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