# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals
from deeppavlov import configs
from deeppavlov.core.commands.infer import build_model

import numpy as np

ecommerce = build_model(configs.ecommerce_skill.tfidf_retrieve1, load_trained=True)
result = ecommerce(['обои'], [[]], [{}])
market_id2yandex_id = dict()

print(result)

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}

search_result = []

with open('out_2.json') as f:
    id_img_dict = json.load(f)


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
    global search_result
    global sessionStorage

    import pprint
    pp = pprint.PrettyPrinter(indent=4)

    requestj = request.json
    pp.pprint(requestj)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    user_id = request.json['session']['user_id']

    if 'payload' in requestj['request']:
        payload = requestj['request']['payload']

        if 'showbasket' in payload:
            basket = sessionStorage[payload['showbasket']]['basket']
            print('BASKET')
            print(basket)
            items = [item for item in search_result[0][0][0] if
                     str(item['ID Маркетплейс']) in basket]
            _list_items(items, response, pay=True)

        if 'details' in payload:
            item_idx = payload['details']
            _display_item(item_idx, response)

        if 'basket' in payload:
            print("add to basket")
            print(sessionStorage)
            if user_id in sessionStorage:
                print("user in sess")
                if 'basket' not in sessionStorage[user_id]:
                    sessionStorage[user_id]['basket'] = []

                sessionStorage[user_id]['basket'].append(payload['basket'])

                print(
                    "========================================================================================================================")
                print(user_id)
                print(sessionStorage[user_id]['basket'])

                logging.info('Response: %r', response)

                response["response"]["text"] = "Товар был добавлен в корзину"
                response["response"]["tts"] = "Товар был добавлен в корзину"
                response["response"]["buttons"] = [{
                    "title": "Показать корзину",
                    "payload": {"showbasket": user_id},
                    "hide": "true"
                }]
                return json.dumps(
                    response,
                    ensure_ascii=False,
                    indent=2
                )

    #  if 'more' in payload:
    else:
        handle_dialog(request.json, response)

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


def _list_items(items, res, pay=False):
    # iglobal search_result
    global market_id2yandex_id

    res['response']['card'] = {'type': 'ItemsList', 'title': '1', 'items': []}

    #    for i in range(idx, idx+min(5, len(search_result[0][0][0]))):
    for i, item in enumerate(items[:5]):

        marketplace_id = str(item['ID Маркетплейс'])
        try:
            # img_id = id_img_dict.get(str(search_result[0][0][0][i]['ID Маркетплейс']), yandex_img_Id)
            img_id = id_img_dict[marketplace_id]
        except KeyError:

            if not marketplace_id in market_id2yandex_id:
                yandex_img_Id = np.random.choice(list(id_img_dict.values()))
                market_id2yandex_id[marketplace_id] = yandex_img_Id
            else:
                yandex_img_Id = market_id2yandex_id[marketplace_id]
            img_id = yandex_img_Id

        #   img_id = id_img_dict.get(str(90051566), "1030494/a7a7418b02613af4f492")

        if item['Название для сайта'] is not None:
            res['response']['card']['items'].append({'title': item['Название для сайта'],
                                                     'image_id': img_id,
                                                     'button': {
                                                         'payload': {'details': i}
                                                     }})

    res['response']['tts'] = "Я нашел для вас " + str(len(res['response']['card'][
                                                              'items'])) + " наименований. Вы можете уточнить поиск воспользовавшись параметрами внизу."
    if pay:
        res['response']['tts'] = "Вот ваша корзина"
        res['response']['buttons'] = [{"title": "Оформить",
                                       "url": "https://market.leroymerlin.ru/basket/",
                                       "hide": 'true'
                                       }]
    else:
        res['response']['buttons'] = [

            {
                "title": "Еще ...",
                "hide": "true"
            },
            {
                "title": "бумага",
                "hide": "true"
            },
            {
                "title": "винил",
                "hide": "true"
            },
            {
                "title": "флизелин",
                "hide": "true"
            }
        ]


#    res['response']['buttons'] = [
#     {
#      "title": "Еще",
#     "payload": {"more":5},
#    "hide": "true"
# }
#  ]


def _display_item(item_idx, res):
    import random
    global search_result
    global market_id2yandex_id

    import re
    desc = search_result[0][0][0][item_idx]['Название для сайта'].split(".")[0][:100]
    desc = re.sub('<[^>]*>', '', desc)
    marketplace_id = str(search_result[0][0][0][item_idx]['ID Маркетплейс'])

    try:
        yandex_id = id_img_dict[marketplace_id]
    except KeyError:
        yandex_id = market_id2yandex_id[marketplace_id]

    res['response']['card'] = {'type': 'BigImage',
                               'title': desc,
                               "description": "Цена: " + str(random.randint(500, 800)) + "р.",
                               'image_id': yandex_id}

    res['response']['buttons'] = [{
        "title": "Добавить в корзину",
        "payload": {'basket': marketplace_id},
        "hide": "true"
    },
        {
            "title": "Открыть на сайте",
            "url": "https://market.leroymerlin.ru/product/oboi-vinilovye-na-flizelinovoy-osnove-avangard-platinum-46-108-02-90002073/",
            "hide": "true"
        }
    ]


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']
    global search_result
    global sessionStorage

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }

        res['response'][
            'text'] = 'Привет, я Ваш персональный помощник по поиску товара! Пожалуйста скажите что Вы ищете.'
        res['response'][
            'tts'] = 'Привет, я Ваш персональный помощник по поиску товара! Пожалуйста скажите что Вы ищете.'
        return

    mes = req['request']['original_utterance'].lower()

    if ('корз' in mes and 'откр' in mes) or ('корз' in mes and 'покажи' in mes):
        if 'basket' in sessionStorage[user_id]:
            print("++++++++++++++++++++++++++++++++++++")
            print(sessionStorage)
            basket = sessionStorage[user_id]['basket']
            print('BASKET')
            print(basket)
            items = [item for item in search_result[0][0][0] if
                     str(item['ID Маркетплейс']) in basket]
            _list_items(items, res, pay=True)
            return
        else:
            res['response']['text'] = "Ваша корзина пуста"
            res['response']['tts'] = "Ваша корзина пуста"
            return

    if 'помощ' in mes:
        res['response']['text'] = "Я Ваш персональный помощник по поиску товара"
        res['response']['tts'] = "Я Ваш персональный помощник по поиску товара"
        return

    if 'доба' in mes and 'корз' in mes:
        if 'basket' not in sessionStorage[user_id]:
            sessionStorage[user_id]['basket'] = []

        sessionStorage[user_id]['basket'].append(str(search_result[0][0][0][0]['ID Маркетплейс']))
        res['response']['text'] = search_result[0][0][0][0][
                                      'Название для сайта'] + " был добавлен в корзину"
        res['response']['tts'] = "Товар был добавлен в корзину"
        res["response"]["buttons"] = [{
            "title": "Показать корзину",
            "payload": {"showbasket": user_id},
            "hide": "false"
        }]
        return

    if 'что ты умее' in mes:
        res['response']['text'] = "Я могу искать товар по каталогу по Вашему запросу"
        return

    if 'привет' in mes or 'здравствуйте' in mes or 'приветствую' in mes or 'как дела' in mes:
        res['response']['text'] = "Приветствую Вас, введите товар который Вы ищете"
        res['response']['tts'] = "Приветствую Вас, введите товар который Вы ищете"
        return

    search_result = ecommerce([mes], [[]], [{}])

    if len(search_result[0][0][0]) > 0:
        items = [item for item in search_result[0][0][0][:5]]
        _list_items(items, res)
    else:
        res['response'][
            'text'] = "К сожалению я не понимаю эту команду. Но могу поискать товар по каталогу, например введите 'обои'"
        res['response'][
            'tts'] = "К сожалению я не понимаю эту команду. Но могу поискать товар по каталогу, например введите 'обои'"
        return


#    res['response']['card']['footer'] = {
#        "text": "Текст блока под изображением.",
#        "button": {
#          "text": "Подробнее",
#          "url": "https://example.com/",
#          "payload": {}
#        }
#      }

# top_element = _extaract_topn_elements(5, search_result[0][0][0])

# res['response'][0]['text'] = "Мы нашли для Вас : %s " % ("\n".join(top_element))
# res['response'][0]['buttons'] = get_suggests(user_id)

# # Обрабатываем ответ пользователя.
# if req['request']['original_utterance'].lower() in [
#     'ладно',
#     'куплю',
#     'покупаю',
#     'хорошо',
# ]:
#     # Пользователь согласился, прощаемся.
#     res['response']['text'] = 'Слона можно найти на Яндекс.Маркете!'
#     return

# # Если нет, то убеждаем его купить слона!
# res['response']['text'] = 'Все говорят, и ты не молчи "%s", а ты купи слона!' % (
#     req['request']['original_utterance']
# )
# res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    global sessionStorage
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


def _extaract_topn_elements(top_n, extract_list):
    if (len(extract_list) >= top_n):
        top_n_elements = [extract_list[i]['Название для сайта'] for i in range(top_n)]
    else:
        top_n_elements = [extract_list[i]['Название для сайта'] for i in range(len(extract_list))]
    return top_n_elements


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)