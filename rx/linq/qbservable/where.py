import ast

from rx.qbservable import Qbservable
from rx.internal import extensionmethod


@extensionmethod(Qbservable, alias="filter")
def where(self, predicate):
    """Filters the elements of an qbservable sequence based on a
    predicate by incorporating the element's index.

    1 - source.filter("lambda value: value < 10")
    2 - source.filter("lambda value, index: value < 10 or index < 10")

    Keyword arguments:
    :param Observable self: Observable sequence to filter.
    :param ast predicate: A function to test each source element
        for a condition; the second parameter of the ast function
        represents the index of the source element.

    :returns: An observable sequence that contains elements from the
    input sequence that satisfy the condition.
    :rtype: Qbservable
    """
    pred = ast.parse(predicate, mode="eval")

    expr = ast.Call(
            func=ast.Attribute(
                value=self.expression,
                attr='where', ctx=ast.Load()),
            args=[pred.body], keywords=[], starargs=None, kwargs=None)

    return self.provider.create_query(expr)
