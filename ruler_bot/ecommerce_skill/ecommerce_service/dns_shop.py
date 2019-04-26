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

from ecommerce_skill.ecommerce_service.base_ecommerce_service import ECommerceService
from bs4 import BeautifulSoup
import requests as req

# DNS is a shitty shop they stop responding with norma HTML and block bots.
class DNSCatalog():

    def search_products(self, query_str):

        # from urllib.parse import urlencode
        # from urllib.request import Request, urlopen

        url = f"https://www.dns-shop.ru/search/?q={query_str}"


        resp = req.get(url)

        soup = BeautifulSoup(resp.text, 'html.parser')


        #####################################################
        # Parsing response:
        import ipdb; ipdb.set_trace()

        # products_list = soup.find_all('div', class_="catalog-items-list view-list")
        products_list = soup.find_all('div', class_="catalog-item-inner catalog-product has-avails")
        results = []
        for each_thing in products_list:
            try:
                # first_image_selector = each_thing.xpath(".//a[@class='ref_goods_n_p']")[0]
                product_url = each_thing.find('a', attrs={"data-role": "product-card-link"})['href']
                image_url = each_thing.find('img')['src']
                # 'https://c.dns-shop.ru/thumb/st1/fit/190/190/bcfdcbecf8e10d60db821d1403dd2e44/ab245de6d88303944c4d293addc6171e66ef93244f8d93767703ff29d80e5210.jpg'



                product_name = each_thing.find_all('h3')[0].text


                try:
                    # DNS SHop does not respond with price, it returns only placeholders,
                    # and really price is filled with Javascript in runtime...
                    product_price = each_thing.find_all('span', attrs={'data-product-param': "price"})[0]

                except Exception as e:
                    # product_price = each_thing.find_all('span', class_='lower-price')[0].text
                    product_price = None
                    # < span class ="price" > < span class ="lower-price" > 2 499 руб.< / span >

                outdict = {
                    "product_url": product_url,
                    "product_image_url": image_url,
                    "product_name": product_name,
                    # "product_brand": product_brand,
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


class DNSShop(ECommerceService):
    """
    Concrete Shop implements interface of ECommerce service
    """

    def __init__(self):
        self.shop_name = "Доктор Айболит"
        self.catalog = DNSCatalog()
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
        """
        return ["Доставка курьером", "почта", "самовывоз"]

    def set_delivery_type(self, delivery_type):
        pass

    def set_delivery_params(self, **params):
        pass

    # Payment
    def show_payment_types(self, payment_type):
        pass

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