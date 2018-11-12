from django.db import models
import django.dispatch

# routes <names of Slots> into implementation classes
from bank_interactions.models.slots import  DesiredCurrencySlot, OptionIntentsSlot, NeedListDocsAndTarifsSlot

##############################################################################################
# TODO make router less ugly,
# TODO autodiscover slot classes by router
slotName2SlotClassRouter = {
    "DesiredCurrencySlot": DesiredCurrencySlot,
    "OptionIntentsSlot": OptionIntentsSlot,
    "NeedListDocsAndTarifsSlot": NeedListDocsAndTarifsSlot


}
slotClass2SlotNameRouter = {val:key for key, val in slotName2SlotClassRouter.items()}
##############################################################################################

class UserSlotProcess(models.Model):
    """
    The process of interaction between user and system about some slot filling

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
    user = models.CharField(max_length=200)

    # we define slots as dynamic classes, so we put class name and then route it into dynamic object:
    slot_codename = models.CharField(max_length=200)

    state = models.CharField(max_length=200, choices=INTERACTION_STATES, default=INIT)
    # ######## END ORM Attrs ################################################################################
    # ###################################################################################################

    @classmethod
    def initialize(cls, user, slot_obj):
        """
        1. Create UserSlotProcess if it is not exist
        2. Declare Signal of the process for announcing completion (slot_filled_signal)

        :param user:
        :param slot_obj:
        :return:
        """
        slot_codename = slotClass2SlotNameRouter[slot_obj.__class__]
        usp, _ = cls.objects.get_or_create(user=user, slot_codename=slot_codename)
        usp.slot_filled_signal = django.dispatch.dispatcher.Signal(providing_args=["user_slot_process"])
        usp.slot = slot_obj
        return usp

    def save(self, *args, **kwargs):
        if not hasattr(self, 'slot_codename'):
            self.slot_codename = slotClass2SlotNameRouter[self.slot.__class__]
        return super(self.__class__, self).save(*args, **kwargs)

    def start(self, ic):
        """

        Start of retrieval process:
        1. Ask Question to user
        2. Connect AnswerReceptor to UserMessageSignal
        3. Set state as Active
        :param ic:
        :return:
        """
        # TODO implement pre-search that avoids questioning if user provided Answer in Dialog Prehistory

        # send question to active dialog
        self.ic = ic
        self.ic.userdialog.send_message_to_user(self.slot.asker_fn())
        self.ic.user_message_signal.connect(self.on_user_response)
        self.state = self.ACTIVE

    def on_user_response(self, *args, **kwargs):
        """
        When user message comes after questioning
        :param text:
        :return:
        """
        # import ipdb; ipdb.set_trace()
        text = kwargs['message']
        from .user_slot import UserSlot
        # import ipdb; ipdb.set_trace()

        if self.slot.can_recept(text):
            result = self.slot.recept(text)
            # validate
            # normalize
            #if ok:
            # put value to user slot and announce completion for arbiter
            self.ic.user_message_signal.disconnect(self.on_user_response)
            # print
            # self.result, _ = UserSlot.objects.get_or_create(self.user, self.slot, result)
            self.result = UserSlot(self.user, self.slot, result)
            # self.result.save()
            self.raw_result = result
            self.state = self.COMPLETED
            self.save()
            self.slot_filled_signal.send(sender=self, user_slot_process=self)
            print("User response filled slot: %s!" % result)

        else:
            # wromg response (
            self.state = self.IGNORED
            self.save()
            print("Unhandled")
    #
    #
    # def __init__(self, user, slot):
    #     self.user = user
    #     self.slot = slot
    #     self.state = self.INIT
    #
    #     # callbacks
    #     self.callback_fns = []
    #
    #     # states = [
    #     #     "init",
    #     #     "value_requested",
    #     #     "completed"
    #     # ]
    #
    #     # state = models.CharField(
    #     #     max_length=2,
    #     #     choices=INTERACTION_STATES,
    #     #     default=INIT
    #     # )
    #
    #     # on completion process may produce results
    #     self.result = None
    #
    # def _complete(self):
    #     self.state = self.COMPLETED
    #     # announse callbacks:
    #     for each_fn in self.callback_fns:
    #         each_fn(self.result)
