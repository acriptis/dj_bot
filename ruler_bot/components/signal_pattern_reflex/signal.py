from components.signal_pattern_reflex.signal_pattern import SignalPattern
from components.signal_pattern_reflex.signal_pattern_reflex_route import SignalPatternReflexRoute


class Signal():
    """

    """
    def __init__(self, **data):
        """
        allows to specify data which will be attached on send
        Args:
            **data:
        """
        self.data = data

    def send(self, **signal_data):
        if self.data:
            # print(self.data)
            # merge signal_data and self.data
            # import ipdb; ipdb.set_trace()
            signal_data.update(self.data)

        sps = SignalPattern.filter_from_signal(**signal_data)
        print(f"Send Signal: {signal_data}")
        count = len(sps)
        print(f"Number of matched patterns for the Signal: {count}")

        srrs = SignalPatternReflexRoute.objects(signal_pattern__in=sps)
        print(f"Number of ReflexRoutes for the SignalPatterns: {srrs.count()}")
        # import ipdb; ipdb.set_trace()

        try:
            for each_srr in srrs:
                each_srr.call_reflex(**signal_data)

        except Exception as e:
            # potentialy this occurs in 2 cases:
            # if we have exception in reflex functor or
            import mongoengine
            if e.__class__ == mongoengine.errors.DoesNotExist:
                # when  reflex was deleted during the looping
                # previous reflexes (on /start event)
                # ok
                return
            else:
                print(e)
                import ipdb; ipdb.set_trace()
                print(e)
                raise e

