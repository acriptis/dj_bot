from django.db import models
# from hello_bot.interactions.models.interactions import Interaction
from interactions.models.interactions import Interaction


class SendTextOperation(Interaction):
    # send to send:
    text = models.CharField(max_length=200)

    # TODO add support of templates and variables filling

    def do(self, ic=None):
        """
        Actual implementation of behaviour
        :return:
        """
        # TODO
        # then user interaction sets its state to completed
        return self.text
