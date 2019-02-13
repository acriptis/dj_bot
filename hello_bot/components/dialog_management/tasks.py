
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
            import ipdb;
            ipdb.set_trace()
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

