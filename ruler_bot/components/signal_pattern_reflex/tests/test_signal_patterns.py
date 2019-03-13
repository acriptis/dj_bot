import unittest
################# Universal Import ###################################################
import sys
import os

SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SELF_DIR)))
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruler_bot.settings")
# #####################################################
import django

django.setup()
###################################################################################################
# just temp vars
from components.signal_pattern_reflex.signal_pattern import SignalPattern
from components.slots.slots_factory import SlotsFactory
from components.receptors.models import Receptor
from components.interactions.models import Interaction, SlottyFormInteraction

from components.signal_pattern_reflex.signal import Signal


class SignalPatternsCreationTest(unittest.TestCase):
    def setUp(self):
        import random
        salt = random.randint(0, 10e6)
        self.user_id = f"perpperonipizza_{salt}"
        from components.user_domains.models.user_domain import UserDomain

        self.user_domain = UserDomain.from_user_id(self.user_id)
        self.receptor, _ = Receptor.get_or_create(class_name='PhrasesMatcher',
                                                  init_args={'phrases': ["СЕКРЕТ"]})
        self.slot_obj = SlotsFactory.produce_free_text_slot(name='username_slot',
                                                            questioner="Как вас зовут?")
        self.interaction_obj1 = SlottyFormInteraction.make_slottfy_form("TestSlottyFormInteraction",
                                                                        [self.slot_obj])
        self.interaction_obj1.save()

    # def test_signal_patterns_creation(self):
    #     """
    #     UserMessageSignal -> Receptor -> ReceptorTriggeredSignal
    #     UserMessageSignal -> Receptor -> x
    #     """
    #
    #     # ################################################################################
    #     # ############### Signal Patterns creation #######################################
    #     # ################################################################################
    #     user_message_pattern1 = SignalPattern(signal_type="UserMessageSignal").save()
    #     user_message_pattern2 = SignalPattern(signal_type="UserMessageSignal", user_domain=self.user_domain).save()
    #     SignalPattern(signal_type="UserMessageSignal", text__contains="песня"
    #                   ).save()
    #     SignalPattern(signal_type="UserMessageSignal", user_domain=self.user_domain
    #                   ).save()
    #     SignalPattern(signal_type="UserMessageSignal", user_domain=self.user_domain
    #                   ).save()
    #     SignalPattern(signal_type="UserMessageSignal"
    #                   ).save()
    #
    #     # Receptor Triggered patterns:
    #     SignalPattern(signal_type="ReceptorTriggeredSignal", receptor=self.receptor
    #                   ).save()
    #     SignalPattern(signal_type="ReceptorTriggeredSignal", receptor=self.receptor
    #                   ).save()
    #
    #     # Slot Filled patterns:
    #     SignalPattern(signal_type="SlotFilledSignal", slot=self.slot_obj
    #                   ).save()
    #     SignalPattern(signal_type="SlotFilledSignal", slot=self.slot_obj,
    #                   user_domain=self.user_domain
    #                   ).save()
    #
    #     # Interactions Completed Patterns
    #     SignalPattern(signal_type="InteractionProcessCompletedSignal",
    #                   interaction=self.interaction_obj1
    #                   ).save()
    #
    #
    #     self._signals_sending()
    #
    #     # ################################################################################
    #     # ############### Signal Patterns connection #####################################
    #     # ################################################################################
    #     user_message_pattern2.connect(self.interaction_obj1.start)
    #     user_message_pattern2.connect(self.receptor)
    #     import ipdb; ipdb.set_trace()
    #
    #     signal = Signal()
    #     payload = {
    #         "signal_type": "UserMessageSignal",
    #         "text": "Привет, СЕКРЕТ",
    #         "user_domain": self.user_domain
    #     }
    #
    #     signal.send(**payload)
    #
    # def _signals_sending(self):
    #     # test signal matching pattern
    #     # ################################################################################
    #     # ############### Signal sending #################################################
    #     # ################################################################################
    #     from components.signal_pattern_reflex.signal import Signal
    #     signal = Signal()
    #     payload = {
    #         "signal_type": "UserMessageSignal",
    #         "text": "Привет",
    #         "user_domain": self.user_domain
    #     }
    #     signal.send(**payload)
    #
    #     payload = {
    #         "signal_type": "ReceptorTriggeredSignal",
    #         "text": "Привет",
    #         "receptor": self.receptor,
    #         "user_domain": self.user_domain
    #     }
    #     signal.send(**payload)
    #
    #     payload = {
    #         "signal_type": "SlotFilledSignal",
    #         "text": "Привет",
    #         "slot": self.slot_obj,
    #         "user_slot_process": "SomeShittyObject",
    #         "user_domain": self.user_domain
    #     }
    #     signal.send(**payload)
    #
    #     payload = {
    #         "signal_type": "InteractionProcessCompletedSignal",
    #         "text": "Привет",
    #         "interaction": self.interaction_obj1,
    #         "user_interaction_process": "SomeShittyObject",
    #         "user_domain": self.user_domain,
    #         "exit_gate": "ExitGate2.OK"
    #     }
    #     signal.send(**payload)

    # #ok
    # def test_user_message_signal_to_receptor(self):
    #     """
    #     UserMessageSignal -> Receptor
    #     Returns:
    #
    #     """
    #     user_message_pattern2 = SignalPattern(signal_type="UserMessageSignal",
    #                                           user_domain=self.user_domain).save()
    #
    #     user_message_pattern2.connect(self.receptor.__call__)
    #
    #     signal = Signal()
    #     payload = {
    #         "signal_type": "UserMessageSignal",
    #         "text": "Привет, СЕКРЕТ",
    #         "user_domain": self.user_domain
    #     }
    #
    #     signal.send(**payload)

    # #ok
    #def test_receptor_signal_to_interaction(self):
    #    """
    #    Receptor -> Interaction.start
    #
    #    Returns:
    #
    #    """
    #    receptor_trig_pattern = SignalPattern(
    #        signal_type="ReceptorTriggeredSignal", receptor=self.receptor).save()
    #    import ipdb;
    #
    #    ipdb.set_trace()
    #
    #    receptor_trig_pattern.connect(self.interaction_obj1.start)
    #
    #    signal = Signal()
    #    payload = {
    #        "signal_type": "ReceptorTriggeredSignal",
    #        "text": "Привет, СЕКРЕТ",
    #        "receptor": self.receptor,
    #        "user_domain": self.user_domain
    #    }
    #
    #    signal.send(**payload)
    #    print(self.user_domain.pending_utterances)
    #
    #    self.user_domain.reload()
    #    print(self.user_domain.pending_utterances)
    #    import ipdb;
    #
    #    ipdb.set_trace()

    # # #ok
    # def test_user_message_signal_to_receptor_to_interaction(self):
    #     """
    #     UserMessageSignal -> Receptor -> Interaction.start
    #     Returns:
    #
    #     """
    #     user_message_pattern2 = SignalPattern(signal_type="UserMessageSignal",
    #                                           user_domain=self.user_domain).save()
    #
    #     user_message_pattern2.connect(self.receptor.__call__)
    #
    #     receptor_trig_pattern = SignalPattern(
    #         signal_type="ReceptorTriggeredSignal", receptor=self.receptor).save()
    #
    #     receptor_trig_pattern.connect(self.interaction_obj1.start)
    #
    #     signal = Signal()
    #     payload = {
    #         "signal_type": "UserMessageSignal",
    #         "text": "Привет, СЕКРЕТ",
    #         "user_domain": self.user_domain
    #     }
    #
    #     signal.send(**payload)
    #     # TODO
    #     # assure that ReceptorTriggeredSignal occured
    #     # assure that Interaction start occured

    def test_signal_pattern_get_or_create(self):
        # import ipdb; ipdb.set_trace()


        user_message_pattern1, created = SignalPattern.get_or_create_strict(
            signal_type="UserMessageSignal", user_domain=self.user_domain)
        user_message_pattern2, created2 = SignalPattern.get_or_create_strict(
            signal_type="UserMessageSignal", user_domain=self.user_domain)
        self.assertTrue(created)
        self.assertFalse(created2)

        user_message_pattern3, created3 = SignalPattern.get_or_create_strict(
            signal_type="UserMessageSignal1",
            user_domain=self.user_domain)
        self.assertTrue(created3)

        user_message_pattern4, created4 = SignalPattern.get_or_create_strict(
            signal_type="UserMessageSignal",
            user_domain=self.user_domain,
            receptor=self.receptor
        )
        self.assertTrue(created4)



# TODO test chains:
#UserMessageSignal -> SlotReceptor -> SlotFilledSignal -> Interaction.slot_completed -> InteractionProcessCompletedSignal

if __name__ == "__main__":
    unittest.main()