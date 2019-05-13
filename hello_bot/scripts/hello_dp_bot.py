################# Universal Import ###################################################
import sys
import os
SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SELF_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
# #####################################################

from components.matchers.matchers import PhrasesMatcher, PhraseGroupsMatcherController

def phrase_matcher_hand_test():
    hi = PhrasesMatcher(phrases=["Hello", "Kek", "Hi"])
    bye = PhrasesMatcher(phrases=["Bye", "Lol", "Exit"])
    disjoint_matchers = [hi, bye]
    pgmc = PhraseGroupsMatcherController(disjoint_matchers)

    # ivanov_ivan_receptor = TrainigPhrasesMatcher(training_phrases=["Ivanov Ivan"])
    print("Kek")
    print(pgmc("Kek"))
    print("Bye")
    print(pgmc("Bye"))
    print("jasdhjsdh")
    print(pgmc("jasdhjsdh"))

    print("Hi Kek, Lol, ki")
    print(pgmc("Hi Kek, Lol, ki"))
    print("***********************")


if __name__=="__main__":
    phrase_matcher_hand_test()
    print("Fin.")