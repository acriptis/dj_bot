from overrides import overrides

from deeppavlov.core.common.registry import register
from deeppavlov.core.data.data_learning_iterator import DataLearningIterator

@register('dialog_state_iterator')
class DialogStateDatasetIterator(DataLearningIterator):
    """
    Iterates over dialog data,
    outputs list of pairs ((utterance tokens, user slots, previous system slots,
    previous dialog state), (dialog state)).
    Inherits key methods and attributes from
    :class:`~deeppavlov.core.data.data_learning_iterator.DataLearningIterator`.
    Attributes:
        train:
        valid:
        test:
    """
    @overrides
    def split(self, *args, **kwargs):
        self.train = self._preprocess(self.train)
        self.valid = self._preprocess(self.valid)
        self.test = self._preprocess(self.test)

    @classmethod
    def _preprocess(cls, turns):
        data = []
        prev_turn = {}
        for u, r in turns:
            if u.get('episode_done'):
                prev_turn = {}
            u_tokens = u['text'].split()
            r_tokens = r['text'].split() if 'text' in r else []
            # u_slots = u.get('slot_values',
            #                cls._biomarkup2dict(u_tokens, u['slots']))
            # r_slots = r.get('slot_values',
            #                cls._biomarkup2dict(r_tokens, r.get('slots', [])))

            x_tuple = (u_tokens, u['slots'], u['intents'],
                       prev_turn.get('system_tokens', []),
                       prev_turn.get('system_slots_bio', []),
                       prev_turn.get('system_acts', []),
                       prev_turn.get('goals', {}))
            y_tuple = (u['goals'])
            prev_turn = {'goals': u['goals'],
                         'system_tokens': r_tokens,
                         'system_slots_bio': r.get('slots', []),
                         'system_acts': r.get('acts', [])}

            data.append((x_tuple, y_tuple))
        return data

    @staticmethod
    def _biomarkup2list(tokens, markup):
        slots = []
        _markup = markup + ['O']
        i = 0
        while i < len(_markup):
            if _markup[i] != 'O':
                slot = _markup[i][2:]
                slot_exclusive_end = i + 1
                while _markup[slot_exclusive_end] == ('I-' + slot):
                    slot_exclusive_end += 1
                slots.append((slot, ' '.join(tokens[i: slot_exclusive_end])))
                i = slot_exclusive_end
            else:
                i += 1
        return slots

    @staticmethod
    def _biomarkup2dict(tokens, markup):
        slots = []
        _markup = markup + ['O']
        i = 0
        while i < len(_markup):
            if _markup[i] != 'O':
                slot = _markup[i][2:]
                slot_exclusive_end = i + 1
                while _markup[slot_exclusive_end] == ('I-' + slot):
                    slot_exclusive_end += 1
                slots.append({'slot': slot,
                              'value': ' '.join(tokens[i: slot_exclusive_end])})
                i = slot_exclusive_end
            else:
                i += 1
        return slots