import aiml
import os


class AIMLSkill():
    """Skill that aggregates AIML scripts and use them to generate answers

    https://www.devdungeon.com/content/ai-chat-bot-python-aiml

    """
    def __init__(self):
        # Create the kernel and learn AIML files
        self.kernel = aiml.Kernel()
        # self.kernel._verboseMode = False
        self._load_scripts()
        from components.signal_pattern_reflex.signal_pattern import SignalPattern
        sp, _ = SignalPattern.get_or_create_strict(signal_type="UserMessageSignal")
        # import ipdb; ipdb.set_trace()
        # this connect must work in runtime, otherwise if we disable skill in Agent Configs it will
        # work anyway...
        # how to solve this problem? - only routes of enabled skills must trigger
        # sp.connect(self.process_step, weak=True, parent_skill=self.__name__)
        sp.connect(self.process_step)

    def _load_scripts(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = cur_dir + "/aiml_scripts"

        # startup_script_path = cur_dir + "/aiml_scripts/std-startup.xml"
        # basic_chat_script_path = cur_dir + "/aiml_scripts/basic_chat.aiml"

        # import ipdb; ipdb.set_trace()
        # learn kernel to all aimls in directory tree:
        for root, dirs, files in os.walk(scripts_dir):
            for file in files:
                if file.endswith(".xml") or file.endswith(".aiml"):
                    file_path = os.path.join(root, file)
                    self.kernel.learn(file_path)
                    # print(file_path)

    def process_step(self, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        utterance_str = kwargs['text']
        user_id = kwargs['user_domain'].user_id
        response = self.kernel.respond(utterance_str, sessionID=user_id)

        if response:
            print("AIML responds:")
            print(response)
            kwargs['user_domain'].udm.DialogPlanner.sendText(response)
        else:
            print("AIML responses silently...")
        return response

    def connect_to_dataflow(self, user_domain_controller):
        """
        Method which prepares stae of the skill for particular UserDomain

        This method used for attaching (persistent) receptors into runtime system

        Args:
            user_domain_controller:

        Returns:

        """
        pass

