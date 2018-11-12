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
        """
        # print("MemoryManager: Implement Me")
        if slot_name not in self.memory.keys():
            raise Exception("Has no memory for key: %s" % slot_name)
        return self.memory[slot_name]

    def put_slot_value(self, slot_name, value):
        """
        Puts particular slot value

        :param slot_name: URI?
        :param value:
        :return:
        """
        self.memory[slot_name] = value
        # print("MemoryManager: Implement Me")
        return self.memory[slot_name]