
# from deeppavlov.skills.pattern_matching_skill import PatternMatchingSkill
# from deeppavlov.core.agent import Agent, HighestConfidenceSelector
# from deeppavlov.core.common.registry import register
# from deeppavlov.core.common.log import get_logger
# from deeppavlov.core.common.file import save_pickle, load_pickle
# from deeppavlov.core.commands.utils import expand_path, make_all_dirs, is_file_exist
# from deeppavlov.core.models.estimator import Component
# from deeppavlov.metrics.bleu import bleu_advanced
# from deeppavlov.core.models.component import Component
import re
import random


class AbstractTextMatcher():
    """
    class for encapsulation of text matching functionality

    matchers check text and return True if match occurs and False otherwise


    """
    def check_match(self, text:str) -> bool:
        pass

    def __call__(self, *args, **kwargs):
        return self.check_match(kwargs['message'])


class TrainigPhrasesMatcher(AbstractTextMatcher):
    def __init__(self, training_phrases, daemon_if_matched=None):
        """

        :param training_phrases:
        :param daemon_if_matched: callable to be called if match occured
        """
        self.training_phrases = training_phrases
        if daemon_if_matched:
            self.daemon_if_matched_fn = daemon_if_matched
        else:
            self.daemon_if_matched_fn = None

    def check_match(self, text, *args, **kwargs):
        """
        Given a text (utterance) it checks if utterance matches the pattern (training phrases)
        :param text:
        :return: True if matches, False otherwise
        """
        result = any([str_pattern in text for str_pattern in self.training_phrases])
        assert result is True or result is False
        # call the daemon
        if result is True:
            # matched
            print("matched on phrases: %s" % self.training_phrases)
            self.daemon_if_matched(text, *args, **kwargs)

        return result

    def daemon_if_matched(self, *args, **kwargs):

        if self.daemon_if_matched_fn:
            self.daemon_if_matched_fn(*args, **kwargs)


class RegExpMatcher(AbstractTextMatcher):
    def __init__(self, regexp_str):
        self.regexp_str = regexp_str
        regexp_matcher_object = re.compile(regexp_str)
        self.regexp_matcher_obj = regexp_matcher_object

    def check_match(self, text, *args, **kwargs):
        """

        :param text:
        :return: True if matches, False otherwise
        """
        result = self.regexp_matcher_obj.search(text, *args, **kwargs)
        assert result is True or result is False
        return result


class MatcherGroup(AbstractTextMatcher):
    """
    Group of Matchers
    class is usefull for merging multiple patterns and example phrases into the same output gate
    """
    def __init__(self, matchers=[]):
        # list of matcher objects
        self.matchers = []

    def add_matcher(self, matcher):
        self.matchers.append(matcher)

    def check_match(self, text, *args, **kwargs):
        """
        checks if any match happens in group
        :param utterance:
        :return: True if any matcher matched, False otherwise
        """
        res = any([pattern.check_match for pattern in self.matchers])
        return res


class PhraseGroupsMatcherController():
    """
    given input utterance it tries to match it through matching groups and announces matched output
    if no matches happens then special output NO_MATCH triggers
    """
    def __init__(self, disjoint_matchers):
        """

        :param disjoint_matchers: list of matchers, so that each matcher result in different output trigger
        """
        self.matcher_groups = disjoint_matchers

        # generate output gate spec:
        self.matcher_2_gate = {each_matcher: idx for idx, each_matcher in enumerate(self.matcher_groups)}

    def process(self, text):
        """
        returns list of indexes of matched output gates
        :param text:
        :return:
        """
        matched_outputs = []
        for idx, each_mathing_group in enumerate(self.matcher_groups):
            if each_mathing_group.check_match(text):
                # matched
                matched_outputs.append(idx)

        if not matched_outputs:
            # default output of NOMATCH
            matched_outputs.append(len(self.matcher_groups))

        return matched_outputs

    def __call__(self, text):
        return self.process(text)

    def add_matcher(self, matcher):
        """
        Adds mathcer to stack of checks and rteturns a signal object which is subscribtable
        :param matcher:
        :return:
        """

    def show_outputs_list(self):
        return
