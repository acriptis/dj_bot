from mongoengine import *

from components.utils.mongoengine_get_or_create_mixin import MongoEngineGetOrCreateMixin


class SignalPatternReflexRoute(Document, MongoEngineGetOrCreateMixin):
    signal_pattern = GenericReferenceField()
    # or:
    # signal_pattern = ReferenceField(SignalPattern)

    reflex = GenericReferenceField()
    #or:
    # reflex = ReferenceField(Reflex)

    # how many times the route was executed
    execution_counter = IntField(default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def call_reflex(self, **signal_data):
        cb_fn = self.reflex.return_prepared_callback()
        # call the callback function:
        cb_fn(**signal_data)
        try:
            # reload model cb_fn may change state of the system!
            self.reload()
            # increment calls counter
            self.execution_counter += 1
            self.save()
        except Exception as e:
            print(e)
            print("Warning: callback deleted?")#
            #import ipdb; ipdb.set_trace()
            print(e)

    def __str__(self):
        return f"[{self.signal_pattern}] -- triggers -> [{self.reflex}]"

    # @classmethod
    # def resolve_callback(cls, callback_fn):
    #     """
    #     Reolves callback method into persistent reflex data structure
    #     Args:
    #         callback_fn: method or function to be resolved
    #
    #     Returns:
    #         ReflexSpecification object
    #     """
    #     # callbacks in the system are either UserSlotProcess's method, or Interactions's method
    #     # or python function?
    #     raise Exception("implement me?!")

    """
        #srr = SignalReflexRoute(user_domain,
        #          signal={
        #              'signal_type': 'UserSlotFilledSignal'
        #              'user_slot_uri': usp.id
        #          },
        #          reflex={'type': 'interaction_method',
        #                   'interaction_codename': inspect.getmembers(each_cb_fn)[7][1],
        #                   'method_name': inspect.getmembers(each_cb_fn)[22][1]}
        #          )
        #

        # inspect.getmembers(inspect.getmembers(callback_fn)[7][1])[24][1]
        # inspect.getmembers(callback_fn)[22][1]
        # inspect.getmembers(callback_fn)[7][1]

        # srr = SignalReflexRoute(user_domain,
        #          signal={
        #                   'signal_type': 'InteractionCompletedSignal', 
        #                   'interaction': self.sfi.name,
        #                   'exit_gate': "ExitGateOk"
        #                  },
        #          reflex={'type': 'interaction_method',
        #                   'interaction_codename': self.name,
        #                   'method_name': 'on_forma_filled'}
        #          )

        # srr = SignalReflexRoute(user_domain
            #          signal={'interaction': self.sfi.name,
            #                     'exit_gate': exit_gate,
            #                  'signal_type': 'COMPLETED_OK'},
            #          reflex={'type': 'interaction_method',
            #                   'interaction_codename': self.name,
            #                   'method_name': 'on_forma_filled'}
            #          )

        #srr = SignalReflexRoute(user_domain,
        #          signal={
        #              'signal_type': 'InteractionCompletedSignal'
        #              'Interaction_uri': self.id?
        #          },
        #          reflex={'type': 'interaction_method',
        #                   'interaction_codename': inspect.getmembers(callback_fn)[7][1],
        #                   'method_name': 'on_forma_filled'}
        #)
        # inspect.getmembers(inspect.getmembers(callback_fn)[7][1])[24][1]
        # inspect.getmembers(callback_fn)[22][1]
        # inspect.getmembers(callback_fn)[7][1]

        # srr = SignalReflexRoute(user_domain,
        #          signal={'signal_type': 'UserMessageSignal'},
        #          reflex={'type': 'user_slot_process_method',
        #                   'slot_codename': self.id,
        #                   'method_name': 'on_user_response'}
        #          )


        # srr = SignalReflexRoute(user_domain,
        #          signal={'signal_type': 'UserMessageSignal'},
        #          reflex={'type': 'user_slot_process_method',
        #                   'slot_codename': self.id,
        #                   'method_name': 'on_user_response'}
        #          )



    """