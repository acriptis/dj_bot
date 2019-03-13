import re
from typing import List


class AbstractTextMatcher():
    """
    class for encapsulation of text matching functionality

    matchers check text and return True if match occurs and False otherwise


    """
    def check_match(self, text:str) -> bool:
        pass

    def __call__(self, *args, **kwargs):
        # return self.check_match(kwargs['message'])
        return self.check_match(*args, **kwargs)


class PhrasesMatcher(AbstractTextMatcher):
    def __init__(self, phrases: List[str], daemon_if_matched=None, case_sensitive=False):
        """

        :param phrases:
        :param daemon_if_matched: callable to be called if match occured
        """
        self.phrases = phrases
        if daemon_if_matched:
            self.daemon_if_matched_fn = daemon_if_matched
        else:
            self.daemon_if_matched_fn = None

        self.case_sensitive = case_sensitive

    def recept(self, text, *args, **kwargs):
        self.check_match(text, *args, **kwargs)

    def check_match(self, text, *args, **kwargs):
        """
        Given a text (utterance) it checks if utterance matches the pattern (training phrases)
        :param text:
        :return: True if matches, False otherwise
        """
        if self.case_sensitive:
            result = any([str_pattern in text for str_pattern in self.phrases])
        else:
            result = any([str_pattern.lower() in text.lower() for str_pattern in self.phrases])
        # assert result is True or result is False
        assert isinstance(result, bool)
        # call the daemon
        if result is True:
            # matched
            print("matched on phrases: %s" % self.phrases)
            self.daemon_if_matched(text, *args, **kwargs)

        return result

    def daemon_if_matched(self, *args, **kwargs):

        if self.daemon_if_matched_fn:
            self.daemon_if_matched_fn(*args, **kwargs)


from deeppavlov import build_model, configs
from components.dataset_iterators.dialog_iterator import DialogStateDatasetIterator


class NERReceptor(AbstractTextMatcher):
    """
    Component that integrates the NERNetwork with the Ruler System
    """
    def __init__(self, daemon_if_matched=None, model_config=None, download=False):
        """
        Args:
            daemon_if_matched: callable to be called if match occured
            model_config: config file, path to file with configuration of DeepPavlov's NER model
            download: bool: if True then it downloads data files required by model, which are
                specified in model config
        """

        if not model_config:
            model_config = configs.ner.ner_rus

        self.ner_model = build_model(model_config, download=download)

        if daemon_if_matched:
            self.daemon_if_matched_fn = daemon_if_matched
        else:
            self.daemon_if_matched_fn = None

    def check_match(self, text, *args, **kwargs):
        """
        Calls DeepPavlov NER for Russian, then converts BOI-markup into dict structures,
        which can be deserialized into ActiveObjects

        Args:
            text: text to parse
            *args:
            **kwargs:

        Returns: result from DeepPavlov model and if specified calls the daemon function

        """

        results = self.ner_model([text])
        res = DialogStateDatasetIterator._biomarkup2dict(results[0][0], results[1][0])
        if res:
            # matched
            print("matched on text: %s" % text)
            print("matched data: %s" % res)
            self.daemon_if_matched(data=res, *args, **kwargs)
        return res

    def daemon_if_matched(self, *args, **kwargs):
        """Calls daemon if it is specified"""
        if self.daemon_if_matched_fn:
            self.daemon_if_matched_fn(*args, **kwargs)


class RegExpMatcher(AbstractTextMatcher):
    """
    Matcher for one regular expression
    """
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


class RegExpGroupMatcher(AbstractTextMatcher):
    """
    Matcher for a group of regexps
    """
    def __init__(self, regexp_str_list):
        self.regexp_str_list = regexp_str_list
        # regexp_matcher_object = re.compile(regexp_str)
        # self.regexp_matcher_obj = regexp_matcher_object

    def check_match(self, text, *args, **kwargs):
        """

        Args:
            text:
            *args:
            **kwargs:

        Returns:
            First match if matches, False otherwise
        """
        matched_intent_pattern = False
        for int_pat in self.regexp_str_list:
            match = re.search(int_pat, text, flags=re.IGNORECASE)
            if match:
                match_response = {
                    "triggered_pattern": int_pat,
                    "match": match,
                    "matched_text_segment": match[0]
                }
                return match_response

        return matched_intent_pattern


class MatcherGroup(AbstractTextMatcher):
    """
    Group of Matchers
    class is usefull for merging multiple patterns and example phrases into the same output gate
    """
    def __init__(self, matchers=None):
        # list of matcher objects
        if matchers is None:
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


class PhraseGroupsMatcherController:
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
        pass

    def show_outputs_list(self):
        return
