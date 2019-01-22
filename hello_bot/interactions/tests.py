from django.test import TestCase

# Create your tests here.

################# Universal Import ###################################################
################# Universal Import ###################################################
import sys
import os

SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SELF_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bank_bot.settings")
# #####################################################
import django
django.setup()
###########################################################################################################
# Test SLOTS
from interactions.models import UserDialog
from django.test import TestCase

# Manual Tests

def test_slot_processing():
    """
    Test case:

    define slot
    start slot process for user
    assure question asked
    imitate user response
    assure receptor grasped data
    and completed UserSlotProcess,

    :return:
    """
    user = "Gena"
    from unittest.mock import MagicMock

    from components.skills.base_skill import InformationController

    ic = InformationController()
    ic.userdialog = UserDialog.objects.create()

    ic.user_message_signal = MagicMock(return_value=3)
    ###########################################################
    # def scenario():
    from bank_consulter_skill.models.slots import DesiredCurrencySlot
    curr_slot_spec = DesiredCurrencySlot()

    goal = {"requires": [curr_slot_spec]}

     # SlotProcess(curr_slot_spec).start(ic, )

    solution = {}

    # whom we ask to start SlotInteraction?

    # pending goals
    # self.goals = [curr_slot_spec]
    from interactions.models.user_slot_process import UserSlotProcess
    usp = UserSlotProcess.initialize(user, curr_slot_spec)
    usp.start(ic)
    usp.save()

    print("Fin")

test_slot_processing()


# ###########################################################################################################
# Slotty Forms Tests:

def test_slotty_form_interaction():
    pass

# test_slotty_form_interaction()