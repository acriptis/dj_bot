class ECommerceService():
    """
    Interface of ECommerce shop API for dialog system.
    """

    def search_products(self, query_str):
        pass

    def search_products_criteria(self, **criteria):
        pass

    def detail_product(self, product_ref):
        pass

    # Cart Management
    def add_product_to_cart(self, product_ref, quantity=1, options=None):
        """
        http://docs.oscarcommerce.com/en/latest/ref/apps/basket.html#oscar.apps.basket.abstract_models.AbstractBasket.add_product
        https://github.com/mirumee/saleor/blob/master/saleor/checkout/forms.py#L30


        Args:
            product_ref:
            quantity:
            options:
        Returns:

        """
        pass

    def show_cart(self):
        pass

    def remove_product_from_cart(self, product_ref, quantity=1, options=None):
        pass


    # Checkout
    # Delivery
    def checkout_cart(self, cart):
        """Action launched when user ready to specify
        delivery/payment options. and transform cart object
        into Order

        Args:
            cart:

        Returns: DeliveryTypesForm

        """
        pass



    def show_delivery_types(self):
        """
            Доставка курьером, почта, самовывоз
        Returns:

        """
        pass

    def set_delivery_type(self, delivery_type):
        """

        Args:
            delivery_type:

        Returns:
            Form for delivery information of the selected delivery type
            DeliveryTypeRequiredSlotsForm
        """
        pass

    def set_delivery_params(self, **params):
        """
        Filled form of delivery params
        Args:
            **params:

        Returns:
            ok
            Cost confirmation Form



        """
        pass

    def confirm_cost(self):
        pass


    # Payment
    def show_payment_types(self, payment_type):
        """

        Args:
            payment_type:

        Returns:
            PaymentTypesForm
        """
        pass

    def set_payment_type(self, payment_type):
        """

        Args:
            payment_type:

        Returns:
            PaymentTypeRequiredSlotsForm
        """
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
        pass

    # PostSale support
    def check_order_status(self, order_ref):
        pass

