from django.contrib import admin
from interactions.models.interactions import Interaction
from interactions.models.user_interaction import UserInteraction
from interactions.models.user_slot_process import UserSlotProcess
from interactions.models.user_slot import UserSlot
from interactions.models.userdialog import UserDialog


class InteractionAdmin(admin.ModelAdmin):

    pass
admin.site.register(Interaction, InteractionAdmin)

class UserInteractionAdmin(admin.ModelAdmin):
    # list_display = ('__str__', 'interaction', 'state')
    list_display = ('interaction', 'state')

admin.site.register(UserInteraction, UserInteractionAdmin)


class UserSlotProcessAdmin(admin.ModelAdmin):
    list_display = ('user', 'slot_codename', 'state')
    pass
admin.site.register(UserSlotProcess, UserSlotProcessAdmin)


class UserSlotAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserSlot, UserSlotAdmin)


class UserDialogAdmin(admin.ModelAdmin):
    # list_display = ('__str__', 'interaction', 'state')
    readonly_fields = ('serialize_dialog_dirty',)
    # readonly_fields = ('__str__', 'serialize_dialog_dirty',)

    # fields = ('__str__', 'serialize_dialog_dirty', )
    fields = ('serialize_dialog_dirty', )

admin.site.register(UserDialog, UserDialogAdmin)
