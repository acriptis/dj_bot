from rest_framework.views import APIView
from rest_framework.response import Response

from bank_consulter_skill.bank_consulter_skill import BankConsulterSkill
from personal_assistant_skills.alarm_setter_skill import AlarmSkill
from personal_assistant_skills.weather_skill import WeatherSkill
from components.agent import AgentSkillInitializer
from root_skill.root_skill import RootSkill
from introduction_skill.introduction_skill import IntroductionSkill
#####################################################################

# key: user_id, value: Agent instance
personal_agents_idx = {}


class AgentRouter():
    """Hacky class to route each dialog to separate Agent instance.

    For each user we have an agent in RAM Memory. If process dies we lose all connections between
    interactions and pending tasks, so reaction of the system after restart is defined.

    """

    @classmethod
    def route_request(cls, user_id, utterance_str):
        global personal_agents_idx
        if user_id not in personal_agents_idx:
            # create new Agent for the user
            print("Create new USER!")

            # personal_agents_idx[user_id] = AgentSkillInitializer(
            #     [IntroductionSkill, BankConsulterSkill, WeatherSkill, AlarmSkill, RootSkill])
            personal_agents_idx[user_id] = AgentSkillInitializer([IntroductionSkill, WeatherSkill])

        bot_resp = personal_agents_idx[user_id](utterance_str)

        return bot_resp


class SkillInteractor(APIView):
    """API View of Skill's endpoint for providing utterances.

    Agent-Skill communication protocol:

    https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#

    Example POST input:
        ```
        {
          "dialogs": [
            {
              "utterances": [
                {
                  "id": "5c65706b0110b377e17eba3f",
                  "text": "давай устроим ЗНАКОМСТВО дорогой ботик",
                  "user_id": "5c65706b0110b377e17eba37",
                  "date_time": "2019-02-14 13:43:07.595000"
                }
              ],
              "user": {
                "id": "5c65706b0110b377e17eba37",
                "user_telegram_id": "0801e781-0b76-43fa-9002-fcdc147d35af"
              }
            },
            {
              "utterances": [
                {
                  "id": "5c65706b0110b377e17eba43",
                  "text": "Когда началась Вторая Мировая?",
                  "user_id": "5c65706b0110b377e17eba37"
                }
              ],
              "user": {
                "id": "5c65706b0110b377e17eba42"
              }
            }
          ]
        }
        ```


    """

    def get(self, request, format=None):
        """
        Just for docs. Use POST method to send data according to protocol:
        https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#
        """
        return Response({
            "text": "use 'POST' method",
            "ref": "https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#"})

    def post(self, request, format=None):
        """
        See docs:
        https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#
        """

        serialized_batch_of_states = request.data

        # ouput of the system is batch of responses for each state in the input batch
        reactions_proposals = []
        if 'dialogs' in serialized_batch_of_states:
            # for each item in dialog run separate instance of agent
            for each_dialog_state in serialized_batch_of_states['dialogs']:
                if 'user' not in each_dialog_state:
                    Response(f"No 'user' attribute in dialog state: {each_dialog_state}")
                if 'id' not in each_dialog_state['user']:
                    Response(f"No 'user.id' attribute in dialog state: {each_dialog_state}")
                if 'utterances' not in each_dialog_state:
                    Response(f"No 'utterances' attribute in dialog state: {each_dialog_state}")

                # validated input
                user_id = each_dialog_state['user']['id']
                last_utterance = each_dialog_state['utterances'][-1]['text']

                state_resp = AgentRouter.route_request(user_id, last_utterance)
                reactions_proposals.append(state_resp)
        else:
            Response("Unsupported format! Need `dialog` attribute!")

        # just to align api spec:
        # https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#heading=h.85j9g7xx30oo
        responses_dict = {'responses': reactions_proposals}
        return Response(responses_dict)

