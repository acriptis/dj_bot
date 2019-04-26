from ecommerce_skill.ecommerce_service.base_ecommerce_service import ECommerceService


class Catalog():
    def __init__(self):

        self.catalog = [
            {
                'id': "1",
                'name': "Нафтизин",
                "description": "лекарство от насморка",
                "price": 235,
                "categories": ["лекарства от рака", "плацебо"]
            },
            {
                'id': "2",
                'name': "Активированный уголь",
                "description": "лекарство от насморка",
                "price": 564,
                "license_required": True
            }
        ]

    def search_products(self, query_str):
        """
        https://market.yandex.ru/search?&text=телефон
        Args:
            query_str:

        Returns:

        """
        return self.catalog
    def search_products_criteria(self, **criteria):
        return self.catalog

    def detail_product(self, product_ref):
        """

        Args:
            product_ref: id of Product item

        Returns:
            dict with the product's features

        """
        filtered_products = list(filter(lambda x: product_ref == x['id'], self.catalog))
        if len(filtered_products) == 1:
            # return data
            return filtered_products[0]
        elif len(filtered_products) == 0:
            raise Exception(f"No product: {product_ref}")
        else:
            raise Exception(f"product is ambiguous: {product_ref}")


class Cart():
    # see:
    # http://docs.oscarcommerce.com/en/latest/ref/apps/basket.html
    def __init__(self):
        # cart is a list of
        #  product bundles structs:
        # {
        #     'product_ref': "1",
        #     'quantity': 2,
        #     'product_params':
        #         {
        #             "color": "red",
        #             "size": "L"
        #         }
        # }

        self.cart = []

    def add_product_to_cart(self, product_ref, quantity=1, product_params={}):
        product_line = {
            'product_ref': product_ref,
            'quantity': quantity,
            'product_params': product_params
        }
        self.cart.append(product_line)
        return product_line

    def show_cart(self):
        return self.cart

    def remove_product_from_cart(self, product_ref, quantity=1):
        raise Exception("Implement me!")


class DrugsShop(ECommerceService):
    """
    Concrete Shop implements interface of ECommerce service
    """

    def __init__(self):
        self.shop_name = "Доктор Айболит"
        self.catalog = Catalog()
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

    def show_delivery_types(self):
        """
            Доставка курьером, почта, самовывоз
        Returns:

        """
        pass

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
