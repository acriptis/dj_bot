from dateparser.search import search_dates

from components.slots.slots import BaseSlotField


class DateTimeSlot(BaseSlotField):
    """
    Slot functionality for retrieving DateTime entities
    Adapter from dateparselib
    """
    def recept(self, text, *args, **kwargs):
        can_recept, results = self._infiltrate(text)
        return results

    def can_recept(self, text, *args, **kwargs):
        can_recept, _ = self._infiltrate(text)
        return can_recept

    def prehistory_recept(self, userdialog):
        """
        Method launched after interaction triggering to consume User's directive about time without explicit question

        In this case we may use the same methods of extraction, although in general case
        Prehistory Analysis differs from ExplicitQuestioningAnswer Anslysis

        Returns only the most recent match!

        :return: tuple (is_recepted, results)
        """
        # get text of prehistory
        # grasp datetimes mentioned before, the most recent datetimes are more confident estimations

        usermessages = userdialog.list_user_messages()
        # search for the recent slot setting (from recent messages to oldest):
        # import ipdb; ipdb.set_trace()

        for each_msg in reversed(usermessages):

            is_recepted, results = self._infiltrate(each_msg)
            if is_recepted:
                return is_recepted, results
            else:
                # no relevant data in this msg
                continue

        return False, None

    def _infiltrate(self, text):
        """
        Given an input text it analyses it and returns a tuple (bool, data)
        Where first element is predicate if infiltartion completed (some relevant tokens are grasped
        from some part of the utterance).
        The second element of tuple is data object, retrieved from utterance

        Currently only one element may be retrieved (so utterance with multiple datetime objects will announce
        only the first result)
        :param text: str
        :return: tuple: (is something recepted:bool, retrieved data object:any)
        1. True, {'raw_subtext': "Завтра в 3 часа", 'value': datetime_obj}
        2. False, None
        """
        # try to infiltrate the slot value
        list_of_result_tuples = search_dates(text)
        if list_of_result_tuples:
            if len(list_of_result_tuples) == 1:
                # ok
                # import ipdb; ipdb.set_trace()

                raw_subtext, datetime_obj = list_of_result_tuples[0]
                return True, {'raw_subtext': raw_subtext, 'value': datetime_obj}
            else:
                # investigate
                print("We have many datetime slot candidates in message we need to resolve this issue!")

                print(list_of_result_tuples)
                # import ipdb;
                # ipdb.set_trace()
        return False, None