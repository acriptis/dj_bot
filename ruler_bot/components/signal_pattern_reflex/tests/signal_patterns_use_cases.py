"""
Just module for analysis of use cases of SignalPatterns
"""
# just temp vars
from components.signal_pattern_reflex.signal_pattern import SignalPattern

receptor = {}
bad_words_receptor = {}
user_domain = {}
slot_obj = {}
slot_obj.start = {}
slot_obj.on_user_response = {}
user_slot_process = {}
user_slot_process.on_user_response = {}

interaction_obj1 = {}
interaction_obj1.start = {}
interaction_obj2 = {}
interaction_obj2.on_slot_filled = {}
interaction_obj2.start = {}

#  Global Connections Ideal Specification:
# Use cases:
# UserMessage Signal Patterns
SignalPattern(signal_type="UserMessageSignal", user_domain="*"
              ).connect(receptor)
SignalPattern(signal_type="UserMessageSignal", user_domain=user_domain
              ).connect(receptor)
SignalPattern(signal_type="UserMessageSignal", text__contains="песня", user_domain="*"
              ).connect(receptor)
SignalPattern(signal_type="UserMessageSignal", user_domain=user_domain
              ).connect(slot_obj.on_user_response)
SignalPattern(signal_type="UserMessageSignal", user_domain=user_domain
              ).connect(user_slot_process.on_user_response)
SignalPattern(signal_type="UserMessageSignal", user_domain="*"
              ).connect(bad_words_receptor)

# Receptor Triggered patterns:
SignalPattern(signal_type="ReceptorTriggeredSignal", receptor=receptor, user_domain="*"
              ).connect(interaction_obj2.start)
SignalPattern(signal_type="ReceptorTriggeredSignal", receptor=receptor, user_domain="*"
              ).connect(slot_obj.start)

# Slot Filled patterns:
SignalPattern(signal_type="SlotFilledSignal", slot=slot_obj, user_domain="*"
              ).connect(interaction_obj2.on_slot_filled)
SignalPattern(signal_type="SlotFilledSignal", slot=slot_obj, user_domain=user_domain
              ).connect(interaction_obj2.on_slot_filled)

# Interactions Completed Patterns
SignalPattern(signal_type="InteractionProcessCompletedSignal", interaction=interaction_obj1
              ).connect(interaction_obj2.start)
SignalPattern(signal_type="InteractionProcessCompletedSignal", interaction=interaction_obj1,
              exit_gate="ExitGateOk"
              ).connect(interaction_obj2.start)