import copy
from collections import OrderedDict

from django.forms.fields import Field


class DeclarativeExitGatesMetaclass(type):
    """Collect ExitGate Signals declared on the base classes."""
    def __new__(mcs, name, bases, attrs):
        # Collect ExitGates from current class.
        current_exit_gates = []

        if 'EXIT_GATES_NAMES_LIST' in attrs.keys():
            # signals are redefined!
            current_exit_gates = attrs['EXIT_GATES_NAMES_LIST']

        else:
            # import from parent class
            pass

        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                current_exit_gates.append((key, value))
                attrs.pop(key)
        attrs['declared_exit_gates'] = OrderedDict(current_exit_gates)

        new_class = super(DeclarativeExitGatesMetaclass, mcs).__new__(mcs, name, bases, attrs)

        # Walk through the MRO.
        declared_exit_gates = OrderedDict()
        for base in reversed(new_class.__mro__):
            # Collect fields from base class.
            if hasattr(base, 'declared_exit_gates'):
                declared_exit_gates.update(base.declared_exit_gates)

            # Field shadowing.
            for attr, value in base.__dict__.items():
                if value is None and attr in declared_exit_gates:
                    declared_exit_gates.pop(attr)

        new_class.base_fields = declared_exit_gates
        new_class.declared_exit_gates = declared_exit_gates

        return new_class

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        # Remember the order in which form fields are defined.
        return OrderedDict()