# Description
This is a pre-alpha version of Rule Based Dialog Bot Framework 
for DeepPavlov project.
The project offers implementation of several dialog skills and
REST API to communicate with DeepPavlov agent system. 
See: https://docs.google.com/document/d/1Z3ZWgyL6xj674Un_9JXIvEPpMjWlhl6ueZOlw5mri8Q/edit#heading=h.iolifv6pxre8 
 
Available Skills (drafts):
1. Introduction Skill. Collects personal slots and after slotfilling provides a recomendation. Use `ЗНАКОМСТВО` keyword in chat to trigger the scenraio.
2. WeatherForecast Skill. Responds for commands with `ПОГОДА` keyword by providing weather
3. AlarmSetterSkill. Sets alarm at specified time. triggering keyword: `НАПОМИНАЛКА`
4. Bank Consulter Skill. Interacts with user for complex Scenario. keyword: `БАНК`
5. Root Skill. Exposes state of slots and agenda (use `план` and `слоты` keywords in chat)
# Deployment
0. create a folder for server and virtualenv (change `temp_hellobot` to your folder name):  
`mkdir temp_hellobot; cd temp_hellobot/`
1. download the source code:  
`git clone https://github.com/acriptis/dj_bot`
2. create a virtual environment:  
`virtualenv .venv3 -p python3`
3. activate virtualenvironment:  
`source .venv3/bin/activate`
4. install requirements:  
`cd hello_bot; pip install -r requirements.txt`
5. Make SQLite3 database migrations:  
`python manage.py migrate`

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

ref: `hello_bot/dp_assistant_rest/input_post__request_example_minimal.json`

Example output:
```
[
    {
        "text": "Как вас зовут?",
        "confidence": 0.75
    },
    {
        "text": "Даже не знаю, что ответить...",
        "confidence": 0.25
    }
]
``` 

# Settings
There is a lot of hardcode in this version.
But you can look into `bank_bot/settings.py` for Django settings.
URLs are specified in `bank_bot/urls.py`

# Domain code
Domain code is placed in skill folders: 
- introduction_skill
- bank_consulter_skill
- personal_assistant_skills
- root_skill 

# Run via Telegram
For running telegram you need to set environmental variable 
`TG_BOT_TOKEN` with you Telegram token.
Then you can run:

`python scripts/start_telegram.py`

# Run tests
`python tests/test_bots.py`