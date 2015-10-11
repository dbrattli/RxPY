from rx import Lock
from .abstractobserver import AbstractObserver
from .observer import Observer


class Qbservable(object):
    """A queryable observable (Qbservable for short)
    """
    def __init__(self, subscribe, provider, expression):
        self._subscribe = subscribe

        self.provider = provider
        self.expression = expression

        self.lock = Lock()

    def subscribe(self, on_next=None, on_error=None, on_completed=None,
                  observer=None):
        if isinstance(on_next, AbstractObserver):
            observer = on_next
        elif not observer:
            observer = Observer(on_next, on_error, on_completed)

        return self._subscribe(observer)

    def __str__(self):
        return str(self.provider)
