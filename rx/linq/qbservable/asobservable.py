from rx import AnonymousObservable, Qbservable
from rx.internal import extensionmethod


@extensionmethod(Qbservable)
def as_observable(self):
    """Hides the identity of an observable sequence.

    :returns: This operator is used to separate the part of the query
    	that's captured as an expression tree from the part that's
    	executed locally.
    :rtype: Observable
    """

    source = self

    def subscribe(observer):
        return source.subscribe(observer)

    return AnonymousObservable(subscribe)
