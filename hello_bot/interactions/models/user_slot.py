from django.db import models
import django.dispatch

class UserSlot(models.Model):
    user = models.CharField(max_length=200)
    # slot = slot
    # self.value = value

    def __init__(self, user, slot, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.slot = slot
        self.value = value
