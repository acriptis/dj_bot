import unittest
################# Universal Import ###################################################
import sys
import os

from components.interactions.models import SlottyFormInteraction
from components.slots.slots_factory import SlotsFactory

SELF_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SELF_DIR))
PREROOT_DIR = os.path.dirname(ROOT_DIR)
print(ROOT_DIR)
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruler_bot.settings")
# #####################################################
import django
django.setup()

from ecommerce_skill.ecommerce_service.base_ecommerce_service import ECommerceService
from bs4 import BeautifulSoup
import requests as req


class WildberryCatalog():

    def search_products(self, query_str):

        # from urllib.parse import urlencode
        # from urllib.request import Request, urlopen

        url = f"https://www.wildberries.ru/catalog/0/search.aspx?search={query_str}"


        resp = req.get(url)

        soup = BeautifulSoup(resp.text, 'html.parser')


        #####################################################
        # Parsing response:
        # import ipdb; ipdb.set_trace()

        products_list = soup.find_all('span', itemtype="http://schema.org/Thing")
        results = []
        for each_thing in products_list:
            try:
                # first_image_selector = each_thing.xpath(".//a[@class='ref_goods_n_p']")[0]
                product_url = each_thing.find_all('a', class_='ref_goods_n_p')[0]['href']
                image_url = each_thing.find_all('img', class_='thumbnail')[0]['src']

                # '//img2.wbstatic.net/c246x328/new/4960000/4968752-1.jpg'


                product_name = each_thing.find_all('span', class_='goods-name')[0].text
                product_brand = each_thing.find_all('strong', class_='brand-name')[0].text
                # product_brand = each_thing.css('strong.brand-name::text').get()

                try:
                    product_price = each_thing.find_all('ins', class_='lower-price')[0].text
                except Exception as e:
                    product_price = each_thing.find_all('span', class_='lower-price')[0].text
                    # < span class ="price" > < span class ="lower-price" > 2 499 руб.< / span >

                outdict = {
                    "product_url": product_url,
                    "product_image_url": image_url,
                    "product_name": product_name,
                    "product_brand": product_brand,
                    "product_price": product_price,
                }
                results.append(outdict)
            except Exception as e:
                print(e)
                import ipdb; ipdb.set_trace()

                print(e)

        return results

    def search_products_criteria(self, **criteria):
        raise Exception("Not Implemented")

    def detail_product(self, product_ref):
        """

        Args:
            product_ref: id of Product item

        Returns:
            dict with the product's features

        """
        resp = req.get(product_ref)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # import ipdb; ipdb.set_trace()
        # products_list = soup.find_all('div', class_="j-description description-text")
        description = soup.find_all('div', class_="j-description description-text")[0].text
        features = soup.find_all('div', class_="pp")
        # TODO parse features?
        # ipdb> soup.find_all('div', class_="pp")[0]
        # <div class="pp"><span><b>Бренд</b></span><span>SALOMON</span></div>
        print(features)
        details_dict = {
            'product_url': product_ref,
            'description': description
        }

        return details_dict

from .base_cart import Cart


class WildberryShop(ECommerceService):
    """
    Concrete Shop implements interface of ECommerce service
    """

    def __init__(self):
        self.shop_name = "Доктор Айболит"
        self.catalog = WildberryCatalog()
        self.cart = Cart()


    # catalog
    def search_products(self, query_string):
        return self.catalog.search_products(query_string)

    def search_products_criteria(self, **criteria):
        return self.catalog.search_products_criteria(**criteria)
    def detail_product(self, product_ref):
        return self.catalog.detail_product(product_ref)

    # Cart Management
    def add_product_to_cart(self, product_ref, quantity=1):
        return self.cart.add_product_to_cart(product_ref, quantity=quantity)

    def show_cart(self):
        return self.cart.show_cart()

    def remove_product_from_cart(self, product_ref, quantity=1):
        return self.cart.remove_product_from_cart(product_ref, quantity=quantity)

    # Checkout
    # Delivery
    def checkout_cart(self, cart):
        """Action launched when user ready to specify
        delivery/payment options. and transform cart object
        into Order

        Args:
            cart:

        Returns:

        """
        pass

    def show_delivery_types(self, *args, **kwargs):
        """
        In general delivery types may depend on the cart's content

            Доставка курьером, почта, самовывоз
        Returns:
            list of delivery methods

            list of dictionaries with delivery types names and Forms
        """
        # slots
        receiver_fio_slot = SlotsFactory.produce_free_text_slot("fio_slot",
                                                                "Напишите ФИО получателя?")
        receiver_phone_slot = SlotsFactory.produce_free_text_slot("phone_slot",
                                                                  "Напишите телефон получателя?")
        receiver_address_slot = SlotsFactory.produce_free_text_slot("address_slot",
                                                                    "Напишите адрес доставки?")

        # Доставка курьером Form
        courier_shipping_info_form = SlottyFormInteraction.make_slottfy_form(
            'courier_shipping_form',
            [receiver_fio_slot, receiver_phone_slot, receiver_address_slot])

        # самовывоз
        pickup_shipping_info_form = SlottyFormInteraction.make_slottfy_form(
            'pickup_shipping_form',
            [receiver_fio_slot, receiver_phone_slot])
        return {
            "Доставка курьером": courier_shipping_info_form,
            "Самовывоз": pickup_shipping_info_form
        }

    def set_delivery_type(self, delivery_type):
        pass

    def set_delivery_params(self, **params):
        pass

    # Payment
    def show_payment_types(self, *args, **kwargs):
        """
        In general payment types may depend on the cart's content and delivery settings

            Оплата наличными (только для доставки курьером и самовывозом)
            Оплата картой
            Оплата биткоинами
        Returns:
            list of delivery methods

            list of dictionaries with delivery types names and Forms
        """

        # slots
        card_number_slot = SlotsFactory.produce_free_text_slot("card_number_slot",
                                                                "Напишите номер вашей карты?")
        card_cvc_code_slot = SlotsFactory.produce_free_text_slot("card_cvc_code_slot",
                                                                  "Напишите CVC код вашей карты?")
        cardholder_name_slot = SlotsFactory.produce_free_text_slot("cardholder_name_slot",
                                                                    "Напишите имя владельца карты?")
        card_valid_until_slot = SlotsFactory.produce_free_text_slot("card_valid_until_slot",
                                                                    "Напишите месяц и год до которых валидна карта?")
        # Оплата картой
        card_payment_info_form = SlottyFormInteraction.make_slottfy_form(
            'card_payment_info_form',
            [card_number_slot, card_cvc_code_slot, cardholder_name_slot, card_valid_until_slot])

        # оплата наличными
        cash_payment_info_form = SlottyFormInteraction.make_slottfy_form(
            'pickup_shipping_form',
            [receiver_fio_slot, receiver_phone_slot])
        return {
            "Оплата картой": card_payment_info_form,
            "Оплата наличными": cash_payment_info_form
        }

    def set_payment_type(self, payment_type):
        pass

    def set_payment_params(self, **params):
        """
        Params depending on payment type
        Args:
            **params:

        Returns:

        """
        pass

    def pay_order(self, cart, delivery_info, payment_info):
        """

        Args:
            cart:
            delivery_info:
            payment_info:

        Returns: Order_ref or raise Exception

        """
        pass

    # PostSale support
    def check_order_status(self, order_ref):
        pass


if __name__ == "__main__":

    wb_c = WildberryCatalog()
    import ipdb; ipdb.set_trace()
    results = wb_c.search_products("тапочки")
    print(results)
    import ipdb; ipdb.set_trace()

    print(results)