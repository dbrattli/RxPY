import ast

from rx.qbservable import Qbservable
from rx.internal import extensionmethod


@extensionmethod(Qbservable, alias="map")
def select(self, selector):
    """Project each element of a qbservable sequence into a new form by
    incorporating the element's index.

    1 - source.map("lambda value: value * value")
    2 - source.map("lambda value, index: value * value + index")

    Keyword arguments:
    :param ast selector: A transform function to apply to
        each source element; the second parameter of the function
        represents the index of the source element.
    :rtype: Qbservable

    Returns a qbservable sequence whose elements are the result of
    invoking the transform function on each element of source.
    """
    sel = ast.parse(selector, mode="eval")

    expr = ast.Call(
            func=ast.Attribute(value=self.expression, attr='select', ctx=ast.Load()),
            args=[sel.body], keywords=[], starargs=None, kwargs=None)

    return self.provider.create_query(expr)
