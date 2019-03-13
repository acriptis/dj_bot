from mongoengine import *
# from django.db.models import DateField, DateTimeField, sql
from components.signal_pattern_reflex.signal_pattern_reflex_route import SignalPatternReflexRoute
from components.signal_pattern_reflex.reflex import ReceptorReflex


class SignalPattern(DynamicDocument):
    """
    Model specifies any signal patterns that can be handled by the system
    """
    meta = {'strict': False}

    signal_type = StringField(required=True)

    # TODO fix the shit with MongoEngine:
    # I need SignalPattern model to be extendable by dynamic attributes which are
    # GenericReferenceField. I can save document with new attr `user_domain` (type:UserDomain):
    #     SignalPattern(signal_type="UserMessageSignal",
    #                   user_domain=user_domain
    #                   ).save()
    # Bit when I restore this object it breakes on iterator:
    #   sps = SignalPattern.objects(signal_type="UserMessageSignal")
    #   for each_sig_pat in sps:
    #       print(each_sig_pat)
    # I can not read it because mongoengine says:
    # `*** mongoengine.errors.FieldDoesNotExist: The fields "{'_ref'}" do not exist on the document "UserDomain"`

    # So finally I decided to inject explicit attributes as GenericReferenceFields, although it
    # makes hard to implement new patterns... So I really need a solution.

    # shitty hack attributes:
    user_domain = GenericReferenceField(required=False)
    receptor = GenericReferenceField(required=False)
    slot = GenericReferenceField(required=False)

    interaction = GenericReferenceField(required=False)
    exit_gate = DynamicField(required=False)

    # TODO make self.get_or_create_strictly() method which given an instance tries to map it with pattern in DB or
    # creates pattern

    @classmethod
    def get_or_create_strict(cls, *args, **kwargs):
        """
        Get or creates with strict matching of attributes.

        Args:
            *args:
            **kwargs:

        Returns:

        """
        # TODO refactor!
        results = cls.objects(*args, **kwargs)
        criterial_keys = kwargs.keys()
        if results:
            # the results that have passed strict matching:
            strictly_matching_results = []
            # import ipdb; ipdb.set_trace()
            for each_result in results:
                # check that result has the same filled attributes as in requested set,
                # (except id attr)

                keys_list = [*each_result._fields.keys()]
                keys_list.remove('id')
                # keys that are not empty in result:
                non_empty_keys = []
                for each_key in keys_list:
                    if each_result[each_key]:
                        # non empty key
                        non_empty_keys.append(each_key)

                # now non empty key-values set must be compared with criterial key-value set
                sym_diff = set(criterial_keys).symmetric_difference(set(non_empty_keys))
                if not sym_diff:
                    # strict matching of arguments set, need to check values
                    for each_ne_key in non_empty_keys:
                        if each_result[each_ne_key] != kwargs[each_ne_key]:
                            break
                    else:
                        # all keys are matched, then we add it into resulting output:
                        strictly_matching_results.append(each_result)

            if strictly_matching_results:
                if len(strictly_matching_results)>1:
                    print("There are multiple strict matches. Investigate!")
                    import ipdb; ipdb.set_trace()
                    raise Exception("multiple strict matches")
                else:
                    return strictly_matching_results[0], False

        # if no results or no strict matches then we need to create object
        instance = cls(*args, **kwargs)
        instance.save()
        return instance, True

    @classmethod
    def filter_from_signal(cls, **signal_data):
        """Given signal instance this method filters patterns from db, that match to the signal.
        Method implements filtration of signal_pattern_candidates that match incoming
        signal object

        Args:
            **signal_data: dict with Signal Schema (signal_type key is required)

        Returns:
            SignalPatterns that match emitted Signal.
        """
        # import ipdb; ipdb.set_trace()

        signal_pattern_candidates = SignalPattern.objects(signal_type=signal_data['signal_type'])
        # TODO is it possible to implement schema agnostic filtering?
        filtered_sps = []
        if signal_data['signal_type'] == "UserMessageSignal":
            for each_sp in signal_pattern_candidates:
                if cls.check_USERMESSAGE_sig_pattern_candidate_with_signal(each_sp, **signal_data):
                    filtered_sps.append(each_sp)

        elif signal_data['signal_type'] == "ReceptorTriggeredSignal":
            for each_sp in signal_pattern_candidates:
                if cls.check_RECEPTORTRIGGERED_sig_pattern_candidate_with_signal(each_sp,
                                                                                 **signal_data):
                    filtered_sps.append(each_sp)

        elif signal_data['signal_type'] == "SlotFilledSignal":
            for each_sp in signal_pattern_candidates:
                if cls.check_SLOTFILLED_sig_pattern_candidate_with_signal(each_sp, **signal_data):
                    filtered_sps.append(each_sp)

        elif signal_data['signal_type'] == "InteractionProcessCompletedSignal":
            for each_sp in signal_pattern_candidates:
                if cls.check_INTERACTIONPROCESSCOMPLETED_sig_pattern_candidate_with_signal(
                        each_sp, **signal_data):
                    filtered_sps.append(each_sp)
            pass
        else:
            print(f"Unrecognized Signal Type {signal_data}!")
            raise Exception("Unrecognized Signal Type")
        return filtered_sps

    @classmethod
    def check_USERMESSAGE_sig_pattern_candidate_with_signal(cls, signal_pattern, **signal_data):
        # check that allowed signal patterns are only with the same user_domain or
        # with user_domain=None

        if not cls._check_user_domain_match(signal_pattern, **signal_data):
            return False

        # check text content matching between pattern and signal?
        return True

    @classmethod
    def check_RECEPTORTRIGGERED_sig_pattern_candidate_with_signal(cls, signal_pattern, **signal_data):
        # check receptor attr in Patterns is the same or None
        # check user_domain attr in Patterns is the same or None
        if not cls._check_user_domain_match(signal_pattern, **signal_data):
            return False

        # check slot attr in Patterns is None or the same as in signal_data
        if signal_pattern.receptor is None:
            # ok
            pass
        elif signal_pattern.receptor == signal_data['receptor']:
            # ok
            pass
        else:
            return False
        return True

    @classmethod
    def check_SLOTFILLED_sig_pattern_candidate_with_signal(cls, signal_pattern, **signal_data):
        # check slot attr in Patterns is the same or None
        # check user_domain attr in Patterns is the same or None

        if not cls._check_user_domain_match(signal_pattern, **signal_data):
            return False

        # check slot attr in Patterns is None or the same as in signal_data
        if signal_pattern.slot is None:
            # ok
            pass
        elif signal_pattern.slot == signal_data['slot']:
            # ok
            pass
        else:
            return False

        return True

    @classmethod
    def check_INTERACTIONPROCESSCOMPLETED_sig_pattern_candidate_with_signal(cls, signal_pattern, **signal_data):
        """
        Checks signal pattern
        Args:
            signal_pattern:
            **signal_data:

        Returns:

        """
        if not cls._check_user_domain_match(signal_pattern, **signal_data):
            return False

        # check if interaction obj in signal_pattern matches signal_data
        if signal_pattern.interaction is None:
            # ok
            pass
        elif signal_pattern.interaction == signal_data['interaction']:
            # ok
            pass
        else:
            return False
        return True

    @classmethod
    def _check_user_domain_match(cls, signal_pattern, **signal_data):
        # check user_domain match
        if not hasattr(signal_pattern, "user_domain"):
            # no attr - no constraint on attribute
            return True

        if signal_pattern.user_domain is None:
            # ok
            pass
        elif signal_pattern.user_domain == signal_data['user_domain']:
            # ok
            pass
        else:
            # fail
            return False

        return True
    # #####################################################################################
    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        """Connects function which may be wrapped into reflex object to the Signal Pattern

        Args:
            receiver:
            sender:
            weak:
            dispatch_uid:

        Returns:

        """
        # 0. convert receiver into ReflexObject with introspection
        # make type switcher:
        from components.signal_pattern_reflex.reflex import ObjectMethodReflex
        if isinstance(receiver, ObjectMethodReflex):
            # 1. case ReflexObject is SlotProcess method
            # 2. case ReflexObject is InteractionProcess method

            srr = self.connect_object_method_reflex(receiver)
            return srr

        import types
        if isinstance(receiver, types.MethodType):
            srr = self.connect_object_method(instance_locator=receiver.__self__, method_name=receiver.__name__)
            return srr

        print("Implement me in connect_<object_type> method!!!")
        print(type(receiver))
        print(receiver.__name__)
        print(receiver.__self__)
        import ipdb; ipdb.set_trace()
        # print("Implement me!")
        raise Exception("Not supported")

    def connect_receptor(self, receptor):
        """
        Connects receptor to signal. Prohibits duplicated signal connections.
        Args:
            receptor: Receptor obj

        Returns: SignalReflexRoute specifying persistent connection

        """

        # TODO user domain is taken from self, is it correct always?
        # Do we need to refactor data scheme to avoid duplicated user_domain and allow flexibility

        receptor_reflex, created = ReceptorReflex.get_or_create(receptor=receptor)

        srr, _ = SignalPatternReflexRoute.get_or_create(signal_pattern=self,
                                                 reflex=receptor_reflex)
        return srr

    def connect_object_method(self, instance_locator, method_name='start'):
        """
        Connects signal with method of object (UserSlotProcess or Interaction).
        Prohibits duplicated signal connections.
        Args:
            instance_locator: object that contains method to call when signal fires
                (Interaction object or UserSlotProcess object)
            method_name: str: name of method in the object to be called when signal fires

        Returns: SignalReflexRoute specifying persistent connection

        """

        # import ipdb; ipdb.set_trace()
        # ??????:
        user_domain = self.user_domain
        # create Reflex for an Interaction's method
        # from components.signal_reflex_routes.models.reflexes import ObjectMethodReflex
        from components.signal_pattern_reflex.reflex import ObjectMethodReflex
        object_method_reflex, _ = ObjectMethodReflex.get_or_create(
            user_domain=user_domain,
            instance_locator=instance_locator,
            method_name=method_name)

        # now test Signal Reflex Route creation
        srr, _ = SignalPatternReflexRoute.get_or_create(signal_pattern=self,
                                                        reflex=object_method_reflex)
        return srr

    def connect_object_method_reflex(self, object_method_reflex, user_domain=None):
        if user_domain:
            srr, _ = SignalPatternReflexRoute.get_or_create(signal_pattern=self,
                                                     reflex=object_method_reflex,
                                                     user_domain=user_domain)
        else:
            # import ipdb; ipdb.set_trace()

            srr, _ = SignalPatternReflexRoute.get_or_create(signal_pattern=self,
                                                     reflex=object_method_reflex)
        return srr

    def disconnect(self, receiver=None, sender=None, dispatch_uid=None):
        """

        Args:
            receiver:
            sender:
            dispatch_uid:

        Returns:

        """
        # TODO make it disconnecting any receiver (not only ObjectMethod reflexes)
        method_name = receiver.__name__
        instance = receiver.__self__
        # from components.signal_reflex_routes.models.reflexes import ObjectMethodReflex
        from components.signal_pattern_reflex.reflex import ObjectMethodReflex
        omr = ObjectMethodReflex.objects(user_domain=instance.user_domain, instance_locator=instance,method_name=method_name)[0]
        if not omr:
            import ipdb; ipdb.set_trace()

            raise Exception("ObjectMethodReflex for receiver: %s is not found. Investigate!")
        # import ipdb; ipdb.set_trace()

        # srrs = SignalPatternReflexRoute.objects(signal_pattern=self, reflex=omr, user_domain=instance.user_domain)
        srrs = SignalPatternReflexRoute.objects(signal_pattern=self, reflex=omr)
        if len(srrs)!=1:
            # strange case investigate
            import ipdb;
            ipdb.set_trace()

            raise Exception("SignalReflexRoute returns multiple Reflexes candidates for receiver: %s. Investigate!")

        srr = srrs[0]
        srr.delete()
        print(f"Receiver {receiver} successfully disconnected!")

    def __str__(self):
         string_with_optional_attrs = f""
         # TODO make attrs agnostic way of representation for extendable scheme of Pattern
         if self.user_domain:
             string_with_optional_attrs += f"|{self.user_domain.id}"
         if self.receptor:
             string_with_optional_attrs += f"|{self.receptor.id}"
         if self.interaction:
             string_with_optional_attrs += f"|{self.interaction.name}"
         if self.slot:
             string_with_optional_attrs += f"|slot.name={self.slot.name}"
         return f"SignalPattern: <{self.signal_type}|{string_with_optional_attrs}>"