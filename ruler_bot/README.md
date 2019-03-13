# Description
This is a alpha version of Rule Based Dialog Bot Framework 
for DeepPavlov project.
The project offers implementation of several dialog skills and
REST API to communicate with DeepPavlov agent system. 
See: https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#heading=h.iolifv6pxre8 
 
Available Skills (drafts):
1. Introduction Skill. Collects personal slots and after slotfilling provides a recomendation. Use `ЗНАКОМСТВО` keyword in chat to trigger the scenraio.
2. Root Skill. Exposes state of slots and agenda (use `план` and `слоты` keywords in chat)
3. Translator Skill. Helps to translate words and phrases from/to different languages 
(English, Russian, Portuguese, Spanish, Japanese). Requires Bing Translator Service keys in [microsoft azure](https://portal.azure.com/#home) 
# Deployment
0. create a folder for server and virtualenv (change `temp_rulerbot` to your folder name):  
`mkdir temp_rulerbot; cd temp_rulerbot/`
1. download the source code:  
`git clone https://github.com/acriptis/dj_bot`
2. create a virtual environment:  
`virtualenv .venv3 -p python3`
3. activate virtualenvironment:  
`source .venv3/bin/activate`
4. install requirements:  
`cd dj_bot/ruler_bot; pip install -r requirements.txt`
5. Make SQLite3 database migrations:  
`python manage.py migrate`
6. If you need Translator Skill you need to provide environmental variable `TRANSLATOR_TEXT_KEY` with secret key for 
BingTranslator API like:
`export TRANSLATOR_TEXT_KEY="123PUTYOURKEY321""`
Fin! Now you can start server and use it!

# Starting Skill REST API Server:
6. Now we can start Django server for REST API:  
`python manage.py runserver 127.0.0.1:8000`

## Agent-Skill REST API interaction
Endpoint for POST requests from Agent Server is `<HOSTNAME>/ruler_call/`.
 
Endpoint expects to receive serialized Batch of States as specified in [DeepPavlov Agent State API](https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#heading=h.iolifv6pxre8).

### Example: 

`http://127.0.0.1:8000/ruler_call/`

Minimal Payload sent by POST method: 
```{
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
          "text": "Как по английски сказать мама?",
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

ref: `hello_bot/dp_assistant_rest/input_post__request_example_minimal.json`

Example output:
```
[
    {
        "text": "Как вас зовут?",
        "confidence": 0.75
    },
    {
        "text": "Mother",
        "confidence": 0.75
    }
]
``` 

# Settings
There is a lot of hardcode in this version.
But you can look into `bank_bot/settings.py` for Django settings.
URLs are specified in `bank_bot/urls.py`

## Enabled skills in REST API
Enabled skills for REST API are specified in `dp_assistant_rest/skill_interactor_api_view.py`. 
They are hardcoded in AgentRouter class.

# Domain code
Domain code is placed in skill folders: 
- introduction_skill
- root_skill 
- translator_skill

# Setup Translator Skill
Translator Skill requires BingTranslator token exported as environmental variable:
`TRANSLATOR_TEXT_KEY`. Assure you providede this variable to environment to enable translator functionality
# Run via Telegram
For running telegram you need to set environmental variable 
`TG_BOT_TOKEN` with you Telegram token.
Then you can run:

`python scripts/start_telegram.py`

# Run tests
`python tests/test_introduction_skill.py`
`python tests/test_translator_skill.py`
`python tests/test_currency_converter_skill.py`

