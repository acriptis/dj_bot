
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