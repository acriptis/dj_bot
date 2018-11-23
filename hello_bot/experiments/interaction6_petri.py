import snakes.plugins
snakes.plugins.load("gv", "snakes.nets", "nets")
# snakes.plugins.load("gv", "snakes.nets")
from snakes.nets import *
from nets import *


class MyObj():
    def __init__(self):
        self.val = 5
        self.DesiredCurrencySlot_value = ["RUB", "USD"]

    def des_cur_value(self):
        return "RUB"

    def des_cur_conatins(self, curr):
        if curr == "USD":
            return True

def petri_net_interaction6():
    myobj = MyObj()
    pnet = PetriNet('Interaction_6')

    # places:
    p_int6start = "Interaction_6.start"
    pnet.add_place(Place(p_int6start, [myobj]))

    p_descur_compl = 'DesiredCurrencySlot.completed'
    pnet.add_place(Place(p_descur_compl, []))

    p_t6rdls = 'TEXT_6_RUB_DOCS_LIST.sent'
    pnet.add_place(Place(p_t6rdls, []))

    p_cirtgdc = 'ClientIsReadyToGiveDocs.completed'
    pnet.add_place(Place(p_cirtgdc, []))

    p_exg6_rr = 'EXIT_GATE_6_RUB_READY'
    pnet.add_place(Place(p_exg6_rr, []))

    p_exg6_ru = 'EXIT_GATE_6_RUB_UNREADY'
    pnet.add_place(Place(p_exg6_ru, []))

    p_exg6_nro = 'EXIT_GATE_6_NONRUB_RESERVATION_OFFLINE'
    pnet.add_place(Place(p_exg6_nro, []))

    # transition elicit(DesiredCurrencySlot)
    transition_name = 'elicit(DesiredCurrencySlot)'
    transition_obj = Transition(transition_name)
    pnet.add_transition(transition_obj)
    pnet.add_input(p_int6start, transition_name, Variable('x'))
    pnet.add_output(p_descur_compl, transition_name, Variable('x'))

    # def transition_factory(transition_name, )

    # transition sendText(TEXT_6_RUB_DOCS_LIST)
    transition_name2 = 'sendText(TEXT_6_RUB_DOCS_LIST)'
    transition_obj2 = Transition(transition_name2, guard=Expression('"RUB" in x.DesiredCurrencySlot_value'))
    pnet.add_transition(transition_obj2)
    pnet.add_input(p_descur_compl, transition_name2, Test(Variable('x')))
    pnet.add_output(p_t6rdls, transition_name2, Variable('x'))

    # transition sendText(TEXT_6_NONRUB_DOCS_INFO)
    transition_name3 = 'sendText(TEXT_6_NONRUB_DOCS_INFO)'
    transition_obj3 = Transition(transition_name3, guard=Expression('x.des_cur_conatins("USD")'))
    pnet.add_transition(transition_obj3)
    pnet.add_input(p_descur_compl, transition_name3, Test(Variable('x')))
    pnet.add_output(p_exg6_nro, transition_name3, Variable('x'))


    # transition elicit(ClientIsReadyToGiveDocs)
    transition_name4 = 'elicit(ClientIsReadyToGiveDocs)'
    transition_obj4 = Transition(transition_name4, guard=Expression("True"))
    pnet.add_transition(transition_obj4)
    pnet.add_input(p_t6rdls, transition_name4, Variable('x'))
    pnet.add_output(p_cirtgdc, transition_name4, Variable('x'))

    # transition sendText(TEXT_6_RUB_READY_REDIRECT)
    transition_name5 = 'sendText(TEXT_6_RUB_READY_REDIRECT)'
    transition_obj5 = Transition(transition_name5, guard=Expression('x.ClientIsReadyToGiveDocs.value == "YES"'))
    pnet.add_transition(transition_obj5)
    pnet.add_input(p_cirtgdc, transition_name5, Variable('x'))
    pnet.add_output(p_exg6_rr, transition_name5, Variable('x'))

    # transition sendText(TEXT_6_RUB_NOT_READY_ASK_RETRY_LATER)
    transition_name6 = 'sendText(TEXT_6_RUB_NOT_READY_ASK_RETRY_LATER)'
    transition_obj6 = Transition(transition_name6, guard=Expression('x.ClientIsReadyToGiveDocs.value == "NO"'))
    pnet.add_transition(transition_obj6)
    pnet.add_input(p_cirtgdc, transition_name6, Variable('x'))
    pnet.add_output(p_exg6_ru, transition_name6, Variable('x'))

    pnet.draw("Interaction_6_1.png")
    print(transition_obj.modes())

    # make transition:
    transition_obj.fire(transition_obj.modes()[0])

    pnet.draw("Interaction_6_2.png")
    print("transition_obj2.modes():")
    print(transition_obj2.modes())
    print("transition_obj3.modes():")
    print(transition_obj3.modes())
    import ipdb; ipdb.set_trace()

    transition_obj2.fire(transition_obj2.modes()[0])
    transition_obj3.fire(transition_obj3.modes()[0])

    transition_obj2.modes()
    pnet.draw("Interaction_6_3.png")

    # import ipdb; ipdb.set_trace()


if __name__ == "__main__":

    petri_net_interaction6()