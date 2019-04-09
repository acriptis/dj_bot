import aiml

class AIMLBot():
    def __init__(self):
        # Create the kernel and learn AIML files
        self.kernel = aiml.Kernel()
        # kernel.learn("std-startup.xml")
        self.kernel.learn("aiml_scripts/std-startup.xml")
        self.kernel.respond("load aiml b")
        pass

    def connect_to_dataflow(self, user_domain_controller):
        # make linking of UserMessageSignal pattern to  AIMLBot kernel
        #TODO
        pass

    def process_step(self, utterance_str, user_id, *args, **kwargs):
        response = self.kernel.respond(utterance_str, sessionID=user_id)
        return response


user_id = "2354"
aiml_bot = AIMLBot()
# Press CTRL-C to break this loop
while True:

    user_utterance_str = input("Enter your message >> ")
    bot_response = aiml_bot.process_step(user_utterance_str, user_id)
    print(bot_response)


