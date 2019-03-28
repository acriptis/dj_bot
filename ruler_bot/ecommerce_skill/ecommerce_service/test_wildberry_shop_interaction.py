# -*- coding: utf-8 -*-
import unittest
################# Universal Import ###################################################
import sys
import os
SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SELF_DIR))
PREROOT_DIR = os.path.dirname(ROOT_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruler_bot.settings")
# #####################################################
import django
django.setup()

# from ecommerce_skill.ecommerce_service.drugs_shop import DrugsShop
from ecommerce_skill.ecommerce_service.wildberry_shop import WildberryShop

if __name__=="__main__":
    shop = WildberryShop()
    results = shop.search_products("лыжи")
    print("search results:")
    print(results)
    # import ipdb; ipdb.set_trace()
    product_details = shop.detail_product(results[0]['product_url'])
    print("product_details:")
    print(product_details)
    product_line = shop.add_product_to_cart(results[0]['product_url'], 2)
    print("product_line:")
    print(product_line)

    cart = shop.show_cart()
    print("cart:")
    print(cart)

    shop.checkout_cart(cart)
