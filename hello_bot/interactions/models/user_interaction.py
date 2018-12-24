from django.db import models
from .interactions import Interaction
from .userdialog import UserDialog

class UserInteraction(models.Model):
    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE)
    # # user no user now)
    #
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

    state = models.CharField(
        max_length=2,
        choices=INTERACTION_STATES,
        default=INIT
    )

    userdialog = models.ForeignKey(UserDialog, on_delete=models.CASCADE)

    def __str__(self):
        return "UserInteractionProcess: User:<%s> Interaction: %s" % (self.userdialog.user, self.interaction)
