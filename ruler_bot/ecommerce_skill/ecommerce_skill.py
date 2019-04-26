from components.interactions.models import Interaction
from components.slots.slots_factory import SlotsFactory
from ecommerce_skill.ecommerce_service.wildberry_shop import WildberryShop
from django.template.loader import render_to_string

class ECommerceSkill():
    def __init__(self):

        self.shop_core = WildberryShop()
        self.search_int, _ = ECSearchInteraction.get_or_create()
        self.add2cart_int, _ = ECAddToCart.get_or_create()
        self.show_cart_int, _ = ECShowCart.get_or_create()
        self.checkout_int, _ = ECCheckoutProcess.get_or_create()

    def connect_to_dataflow(self, udc):
        pass


_shop_core = WildberryShop()

class ECommerceMixin():
    @property
    def shop_core(self):
        global _shop_core
        if _shop_core:
            self._shop_core = _shop_core
        else:
            raise Exception("No _shop_core")
        return self._shop_core


class ECSearchInteraction(Interaction, ECommerceMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connect_receptor(receptor_type="PhrasesMatcher",
                               init_args={'phrases': ["найди", "хочу"]},
                               callback_fn=self.start)

    def connect_to_dataflow(self, udc):
        pass

    def start(self, *args, **kwargs):
        # parse search intent
        # request EShop search API
        # retrieve results
        # verbalise them to user
        # set local context
        query = kwargs['text']

        # ################################################################################
        # Receptor post processing
        # TODO move into perceptoir class
        #
        phrase = "найди мне"
        if phrase in kwargs['text']:
            query = query.replace(phrase, "").strip()

        # ################################################################################
        results = self.shop_core.search_products(query)
        if len(results)>5:
            # reduce results set
            results = results[0:5]
            # TODO allow pagination
        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm
        udm.DialogPlanner.sendText("Вот что я нашел:")

        # wrap results into DialogTemplate:
        context = {'products_list': results}
        rendered = render_to_string('products_list.html',
                                    context)


        udm.MemoryManager.put_slot_value("ecommerce__last_context", "products_list")
        udm.MemoryManager.put_slot_value("ecommerce__products_list", results)
        udm.DialogPlanner.sendText(rendered)
        # set context with list of results to enable adding to cart by ordinal product references


class ECDetailProduct(Interaction, ECommerceMixin):
    """
    Interaction to show product details
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connect_receptor(receptor_type="PhrasesMatcher",
                               init_args={'phrases': ["детализируй", "покажи"]},
                               callback_fn=self.start)

    def connect_to_dataflow(self, udc):
        pass

    def start(self, *args, **kwargs):
        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm
        # ######################################################################
        # retrieve product reference
        from ecommerce_skill.product_ref_perceptor.product_ref_perceptor import \
            ProductReferenceExtractor
        pre = ProductReferenceExtractor()
        res = pre(**kwargs)
        print(res)
        # ######################################################################

        # and run action detail(product_ref)
        # decorate results
        # say them
        # set default product reference slot for AddToCart action?
        product_ref = "someproduct_uri"

        udm.MemoryManager.put_slot_value("ecommerce__last_context", "product_detail")
        udm.MemoryManager.put_slot_value("ecommerce__product_detail", product_ref)


class ECAddToCart(Interaction, ECommerceMixin):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self._connect_receptor(receptor_type="RegExpGroupMatcher",
                               init_args={'regexp_str_list': ["добавь .* в корзину"]},
                               callback_fn=self.start)

    def connect_to_dataflow(self, udc):
        pass

    def start(self, *args, **kwargs):
        # parse intent and retrieve products to add

        # require products reference receptor
        # product_reference_receptor.recept(kwargs)
            # recept from the message
            # if not set recept from context (if context was with detail of product then
            #   take that product)
            # if not retrievable from context run active questioning process with ProductToAddInCartSlot

        # request EShop API
        # retrieve status results
        # verbalise them to user
        # update local context of cart
        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm


        # ######################################################################
        # retrieve product reference
        from ecommerce_skill.product_ref_perceptor.product_ref_perceptor import \
            ProductReferenceExtractor
        pre = ProductReferenceExtractor()
        referenced_products = pre(**kwargs)
        if referenced_products:
            print("Detected referenced products!")
            print(referenced_products)
            for each_product in referenced_products:
                # TODO add multiple products adding support
                product_line = self.shop_core.add_product_to_cart(each_product, quantity=1)
                udm.DialogPlanner.sendText(f"Добавил в корзину {product_line}")

        # ######################################################################


class ECShowCart(Interaction, ECommerceMixin):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


        self._connect_receptor(receptor_type="PhrasesMatcher",
                               init_args={'phrases': ["корзина", "покажи корзину"]},
                               callback_fn=self.start)

    def connect_to_dataflow(self, udc):
        pass

    def start(self, *args, **kwargs):
        # request CartAPI
        cart_view = self.shop_core.show_cart()

        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm

        # # wrap results into DialogTemplate:
        # context = {'products_list': results}
        # rendered = render_to_string('products_list.html',
        #                             context)

        udm.DialogPlanner.sendText(str(cart_view))


class ECCheckoutProcess(Interaction, ECommerceMixin):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self._connect_receptor(receptor_type="PhrasesMatcher",
                               init_args={'phrases': ["к покупке"]},
                               callback_fn=self.start)


    def start(self, *args, **kwargs):
        """
        Starts process of filling the form with Delivery info and Payment Info
        Args:
            *args:
            **kwargs:

        Returns:

        """
        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm
        udm.DialogPlanner.sendText("Начнем процесс покупки")

        # TODO start delivery specification form
        # retrieve cart from context?
        # validate cart
        # request shop_core for DeliveryTypesForm
        # set receptor for delivery types

        # ######################################################################################
        # form with delivery options and slots
        delivery_types_forms = self.shop_core.show_delivery_types()

        categories_and_synsets = {delivery_type: [delivery_type]
                                  for delivery_type, delivery_form in delivery_types_forms.items()}

        delivery_options= delivery_types_forms.keys()
        delivery_types_slot = SlotsFactory.produce_categorical_slot(
            "delivery_types_slot", f"Какой способ доставки вас интересует? Возможные варианты: {delivery_options}",
            categories_domain_specification=categories_and_synsets)
        ########################################################################################

        print("ENQUEUE delivery_types_slot into Agenda!")

        # then it triggers on each SlotFilledSignal insted of delivery_types_slot
        udm.DialogPlanner.plan_process_retrieve_slot_value_with_slot_spec_instance(
            delivery_types_slot, priority=10,
            callback_fn=self.on_delivery_type_answered,
            duplicatable=False, target_uri=delivery_types_slot.get_name())

    def on_delivery_type_answered(self, *args, **kwargs):
        # given a delivery type request shop core for DeliveryTypeForm with slots
        # push slotty form into Agenda
        # connect on complete
        # import ipdb; ipdb.set_trace()

        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm
        udm.DialogPlanner.sendText("on_delivery_type_answered!")

        delivery_types_forms = self.shop_core.show_delivery_types()
        # TODO refactor naming linking to avoid spelling errors
        chosen_types = udm.MemoryManager.get_slot_value("delivery_types_slot")
        if chosen_types:
            if chosen_types[0] in delivery_types_forms.keys():
                # ok
                slotty_form_for_client = delivery_types_forms[chosen_types[0]]
                # enqueue form for filling delivery address
                # import ipdb; ipdb.set_trace()

                udm.DialogPlanner.enqueue_interaction(
                    slotty_form_for_client, priority=10,
                    callback_fn=self.on_delivery_form_filled)
            else:
                raise Exception("Chosen types not in Available types of delivery form types")
        else:
            raise Exception("No Chosen types")
        # import ipdb; ipdb.set_trace()

    def on_delivery_form_filled(self, *args, **kwargs):
        # request shop_core for PaymentTypesForm
        # set receptor for Payment types
        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm
        udm.DialogPlanner.sendText("on_delivery_form_filled!")
        # start payment interaction
        # offer payment types

        # ######################################################################################
        # ##### PAYMENT stage ##################################################################
        # ######################################################################################
        from ecommerce_skill.payment_form_interaction import PaymentFormInteraction
        pfi = PaymentFormInteraction.make_slottfy_form("PaymentFormInteraction")
        # import ipdb; ipdb.set_trace()

        udm.DialogPlanner.enqueue_interaction(
            pfi, priority=10,
            callback_fn=self.on_payment_form_interaction_completed)
        udm.DialogPlanner.sendText("PaymentFormInteraction enqueued!")
        user_domain.agenda.save()


    def on_payment_form_interaction_completed(self, *args, **kwargs):
        # try to Pay with form data?
        # submit order to shop_core
        # announce client that everything is fine
        # provide him and order id

        # set up post sale receptors
        user_domain = kwargs['user_domain'].reload()
        udm = user_domain.udm
        udm.DialogPlanner.sendText("on_payment_form_interaction_completed! We can transfer the order to ShopCore")
        # TODO populate all data of the order:
        # data = {
        #     'cart': cart_repr,
        #     'delivery': delivery_info,
        #     'payment': payment_info,
        #     'client': client
        # }
