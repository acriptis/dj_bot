
class MongoEngineGetOrCreateMixin:
    """Class that injects get_or_create functionality in mongoengine ORM models.

    """

    @classmethod
    def get_or_create(cls, *args, **kwargs):
        # import ipdb; ipdb.set_trace()

        results = cls.objects(*args, **kwargs)

        if results:
            if len(results) > 1:
                raise Exception(
                    f"Multiple instances found for {cls.__name__}!")
            elif len(results) == 1:
                return results[0], False
        else:
            instance = cls(*args, **kwargs)
            instance.save()
            return instance, True
