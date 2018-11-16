class MemoryManager():
    def __init__(self, ic):
        self.ic=ic

        # key value data structure:
        self.memory = {}

    def get_slot_value(self, slot_name):
        """
        Given a slot name returns its value or raises Exception
        :param slot_name: str?
        :return:
            value of the memory element
            :keywordraise Exception (no value)
        """
        # print("MemoryManager: Implement Me")
        if slot_name not in self.memory.keys():
            raise Exception("Has no memory for key: %s" % slot_name)
        return self.memory[slot_name]

    def get_slot_value_quite(self, memo_uri):
        """
        in contrast to  get_slot_value method this one doesn't rise exception if memory is absent just returns None
        :param slot_name:
        :return: value or None if no memory for uri
        """
        try:
            value = self.get_slot_value(memo_uri)
            return value
        except Exception as e:
            print(e)
            return None

    def put_slot_value(self, slot_name, value, uri=None):
        """
        Puts particular slot value

        :param slot_name: URI?
        :param value:
        :return:
        """
        self.memory[slot_name] = value
        # print("MemoryManager: Implement Me")
        return self.memory[slot_name]