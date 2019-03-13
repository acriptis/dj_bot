from components.interactions.models import Interaction


class ConvertCurToCurInteraction(Interaction):
    """
    Interaction responsible for detection of Intent to convert amount in one currency into
    another currency.

    Phrases:
    Сколько рублей в долларе?
    1000 долларов это сколько рублей?
    Почем доллары?
    """

    def __init__(self, *args, **values):
        #TODO
        super().__init__(*args, **values)
