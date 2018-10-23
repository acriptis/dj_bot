import weakref
import threading
import traceback
import inspect
import logging

class Signal():
    """callback functions (so called slots) can be connected to a signal and
    will be called when the signal is called (Signal implements __call__).
    The slots receive two arguments: the sender of the signal and a custom
    data object. Two different threads won't be allowed to send signals at the
    same time application-wide, concurrent threads will have to wait until
    the lock is releaesed again. The lock allows recursive reentry of the same
    thread to avoid deadlocks when a slot wants to send a signal itself."""

    _lock = threading.RLock()
    signal_error = None

    def __init__(self):
        self._functions = weakref.WeakSet()
        self._methods = weakref.WeakKeyDictionary()

        # the Signal class itself has a static member signal_error where it
        # will send tracebacks of exceptions that might happen. Here we
        # initialize it if it does not exist already
        if not Signal.signal_error:
            Signal.signal_error = 1
            Signal.signal_error = Signal()

    def connect(self, slot):
        """connect a slot to this signal. The parameter slot can be a funtion
        that takes exactly 2 arguments or a method that takes self plus 2 more
        arguments, or it can even be even another signal. the first argument
        is a reference to the sender of the signal and the second argument is
        the payload. The payload can be anything, it totally depends on the
        sender and type of the signal."""
        if inspect.ismethod(slot):
            instance = slot.__self__
            function = slot.__func__
            if instance not in self._methods:
                self._methods[instance] = set()
            if function not in self._methods[instance]:
                self._methods[instance].add(function)
        else:
            if slot not in self._functions:
                self._functions.add(slot)

    # def __call__(self, sender, data, error_signal_on_error=True):
    def __call__(self, sender, *args, **kwargs):
        """dispatch signal to all connected slots. This is a synchronuos
        operation, It will not return before all slots have been called.
        Also only exactly one thread is allowed to emit signals at any time,
        all other threads that try to emit *any* signal anywhere in the
        application at the same time will be blocked until the lock is released
        again. The lock will allow recursive reentry of the seme thread, this
        means a slot can itself emit other signals before it returns (or
        signals can be directly connected to other signals) without problems.
        If a slot raises an exception a traceback will be sent to the static
        Signal.signal_error() or to logging.critical()"""
        with self._lock:
            sent = False
            errors = []
            for func in self._functions:
                try:
                    func(sender, *args, **kwargs)
                    sent = True

                except: # pylint: disable=W0702
                    errors.append(traceback.format_exc())

            for instance, functions in self._methods.items():
                for func in functions:
                    try:
                        func(instance, sender, *args, **kwargs)
                        sent = True

                    except: # pylint: disable=W0702
                        errors.append(traceback.format_exc())

            for error in errors:
                # if error_signal_on_error:
                Signal.signal_error(self, (error), False)
                # else:
                logging.critical(error)

            return sent
