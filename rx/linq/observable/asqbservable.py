from rx import ObservableQuery, Observable
from rx.internal import extensionmethod


@extensionmethod(Observable)
def as_qbservable(self):
    """Convert an in-memory observable sequence into a Qbservable
    sequence with an expression tree representing the source sequence.

    :returns: A qbservable sequence.
    :rtype: Qbservable
    """

    return ObservableQuery(source=self)
