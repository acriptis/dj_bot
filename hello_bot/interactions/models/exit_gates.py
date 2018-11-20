
class ExitGate():
    """
    ExitGate class for interactions completions

    String (Signal-like object in future) used for specification of potential exits from interactions.
    Triggering of particular ExitGate may trigger particular reactions of
    the system like starting/enabling new interaction processes alongside Scenario.

    Currently used as string constant in Interaction objects
    """
    def __init__(self, name):
        self.name=name

    def __str__(self):
        return self.name
