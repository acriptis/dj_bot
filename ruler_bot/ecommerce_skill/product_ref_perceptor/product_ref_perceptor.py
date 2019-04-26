from components.matchers.matchers import RegExpGroupMatcher, PhraseGroupsMatcherController
# from components.slots.slots import CategoricalSlot
#
#
# # class OrdinalNumberReceptor(CategoricalSlot):
# #     """
# #     The simple class for detecting Ordinal Numbers in Russian
# #     """
# #     pass
# from components.slots.slots_factory import SlotsFactory
#
# ordinal_number_slot = SlotsFactory.produce_categorical_slot(
#     'ordinal_numbers_slot',
#     questioner=None,
#     categories_domain_specification={
#         "1": ["первый", "перв"]
#     }
# )

# ##############################################################################################
# cardinal numbers matcher
first_item = RegExpGroupMatcher(regexp_str_list=["перв.{1,3}"])
second_item = RegExpGroupMatcher(regexp_str_list=["втор.{1,3}"])
third_item = RegExpGroupMatcher(regexp_str_list=["трет.{1,4}"])
fourth_item = RegExpGroupMatcher(regexp_str_list=["четверт.{1,3}"])
fifth_item = RegExpGroupMatcher(regexp_str_list=["пят.{1,3}"])
disjoint_matchers = [first_item, second_item,third_item, fourth_item, fifth_item]
cardinal_number_detector = PhraseGroupsMatcherController(disjoint_matchers)
# ##############################################################################################


class ProductReferenceExtractor():
    """
    The class that encapsulates complexity of extraction of product reference from DialogContext
    """

    def extract_product_references_from_message(self, message_str, context_products_list):
        """

        Args:
            message:

        Returns:

        """
        pass

    def map_uttered_product_reference_to_concept(self, uttered_product_reference, context_products_list):
        """

        Args:
            uttered_product_reference: Пурпурная туфелька / третий товар
            context_products_list: [
            ]

        Returns:

        """
        [
            {'product_name': "Туфелька kitty",
             'product_brand': "Lui Vitton",
             'description': "Изыскаянная туфелька розового и малинового цвета",
             'local_index': 1,
             'product_url': "http://some.url/2334",
             },
            {'product_name': "Туфелька GangBang",
             'product_brand': "twenty hundred tonns",
             'description': "Ошеломительная туфелька пурпурного цвета",
             'local_index': 2,
             'product_url': "http://some.url/23342",
             },
        ]
        pass

    def __call__(self, text, *args, **kwargs):
        """
        Retrieve product reference from dialog context
        Args:
            *args:
            **kwargs:

        Returns:
                list of referenced products in text
                list of dicts.
                Example:
                    [
                        {'product_url': 'https://www.wildberries.ru/catalog/244853/detail.aspx?targetUrl=ES',
                        'product_image_url': '//img1.wbstatic.net/c246x328/new/240000/244853-1.jpg',
                        'product_name': "Набор соль-перец ''Туфельки''",
                        'product_brand': 'Pavone /',
                        'product_price': ' 1\xa0248\xa0руб.'}
                    ]
        """

        user_domain = kwargs['user_domain']
        udm = user_domain.udm
        last_context = udm.MemoryManager.get_slot_value_quite("ecommerce__last_context")
        if last_context == "product_detail":
            # add it to cart without any analysis???
            # rude but works in many cases)
            print("PRODUCT DETAILS is last context. Product in Focus is:")
            print(udm.MemoryManager.get_slot_value_quite("ecommerce__product_detail"))
            import ipdb; ipdb.set_trace()

            print(text)
        if last_context == "products_list":
            # try to map text to results list
            print("PRODUCTS LIST is last context. Product LIST is:")
            products_list = udm.MemoryManager.get_slot_value_quite("ecommerce__products_list")
            print(products_list)
            matched_indexes, matched_results = cardinal_number_detector.process(text)
            referenced_products = []
            if matched_indexes:
                # something matched
                if len(matched_indexes)==1:
                    # ok we have one cardinal number
                    # suppose it is reference to a product item in the list of products
                    referenced_product = products_list[matched_indexes[0]]
                    referenced_products.append(referenced_product)
                    return referenced_products
                else:
                    # several cardinals...
                    print("Investigate multiple cardinal matches")
                    import ipdb; ipdb.set_trace()

                    print("Investigate multiple cardinal matches")
            print(text)
            pass
        print("No context Investigate me, how I am here?!")
        # import ipdb; ipdb.set_trace()

        print("No context Investigate me, how I am here?!")