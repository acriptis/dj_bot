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

from ecommerce_skill.ecommerce_service.drugs_shop import DrugsShop

if __name__=="__main__":
    drugshop = DrugsShop()
    results = drugshop.search_products("лыжи")
    print(results)
    import ipdb; ipdb.set_trace()
    product_details = drugshop.detail_product(results[0]['id'])
    print(product_details)
    product_line = drugshop.add_product_to_cart(results[0]['id'], 2)
    print(product_line)

    cart = drugshop.show_cart()
    print(cart)

    drugshop.checkout_cart(cart)
