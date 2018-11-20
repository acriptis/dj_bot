from django.db import models
import django.dispatch
#
# # routes <names of Slots> into implementation classes
# from bank_interactions.models.slots import DesiredCurrencySlot, OptionIntentsSlot, NeedListDocsAndTarifsSlot, \
#     ClientServiceRegionSlot, ClientIsResidentRFSlot, ClientPropertyTypeSlot, ClientAgreeWithServicePackConditionsSlot
#
# ##############################################################################################
# # TODO make router less ugly,
# # TODO autodiscover slot classes by router
# slotName2SlotClassRouter = {
#     "DesiredCurrencySlot": DesiredCurrencySlot,
#     "OptionIntentsSlot": OptionIntentsSlot,
#     "NeedListDocsAndTarifsSlot": NeedListDocsAndTarifsSlot,
#     "ClientIsResidentRFSlot": ClientIsResidentRFSlot,
#     "ClientServiceRegionSlot": ClientServiceRegionSlot,
#     "ClientPropertyTypeSlot": ClientPropertyTypeSlot,
#     "ClientAgreeWithServicePackConditionsSlot": ClientAgreeWithServicePackConditionsSlot
#
#
# }
# slotClass2SlotNameRouter = {val:key for key, val in slotName2SlotClassRouter.items()}
# ##############################################################################################

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
        # slot_codename = slotClass2SlotNameRouter[slot_obj.__class__]
        slot_codename = slot_obj.get_name()

        usp, _ = cls.objects.get_or_create(user=user, slot_codename=slot_codename)
        # signal emitted when slot is filled
        usp.slot_filled_signal = django.dispatch.dispatcher.Signal(providing_args=["user_slot_process"])
        # TODO how to restore signal connections? (So listeners will be notified)
        usp.slot = slot_obj
        return usp

    def save(self, *args, **kwargs):
        # return
        # import ipdb; ipdb.set_trace()
        #
        if not hasattr(self, 'slot_codename'):
            # self.slot_codename = slotClass2SlotNameRouter[self.slot.__class__]
            self.slot_codename = self.slot.get_name()
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
        self.save()

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

            # import ipdb; ipdb.set_trace()

            self.slot_filled_signal.send(sender=self, user_slot_process=self)
            self.save()
            print("User response filled slot: %s!" % result)

        else:
            # wrong response (
            self.state = self.IGNORED
            self.save()
            # Greed reAsk Strategy:
            print("Slot Unhandled (Greed reAsk Strategy). ReAsking...")
            self.ic.userdialog.send_message_to_user(self.slot.asker_fn() + " (Greed ReAsk Strategy)")

            # print("Slot Unhandled (Passive waiting Strategy)")
            # TODO implement attachement of Exception Strategy:
            # 1. Forced Slot: ReAsk Urgently
            # 2. Passive Waiting, but we need to attach handler
            # here
