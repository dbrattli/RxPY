from rx import Lock
from .abstractobserver import AbstractObserver
from .observer import Observer


class Qbservable(object):
    def __init__(self, subscribe, provider, expression):
        self._subscribe = subscribe

        self._provider = provider
        self.expression = expression

        self.lock = Lock()

    def subscribe(self, on_next=None, on_error=None, on_completed=None,
                  observer=None):
        if isinstance(on_next, AbstractObserver):
            observer = on_next
        elif not observer:
            observer = Observer(on_next, on_error, on_completed)

        return self._subscribe(observer)

    @property
    def provider(self):
        return self._provider

    def __str__(self):
        print("Qbservable:__str__")
        return str(self.provider)
