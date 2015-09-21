import ast

from rx.qbservable import Qbservable
from rx.internal import extensionmethod


@extensionmethod(Qbservable, alias="map")
def select(self, selector):
    """Project each element of an observable sequence into a new form by
    incorporating the element's index.

    1 - source.map(lambda value: value * value)
    2 - source.map(lambda value, index: value * value + index)

    Keyword arguments:
    :param Callable[[Any, Any], Any] selector: A transform function to apply to
        each source element; the second parameter of the function represents
        the index of the source element.
    :rtype: Observable

    Returns an observable sequence whose elements are the result of
    invoking the transform function on each element of source.
    """
    print("****")
    print(ast.dump(self.expression))

    sel = ast.parse(selector, mode="eval")

    expr = ast.Expression(
        body=ast.Call(
            func=ast.Attribute(
                value=ast.Name(id=self, ctx=ast.Load()),
                attr='select', ctx=ast.Load()),
            args=[sel], keywords=[], starargs=None, kwargs=None))

    print(ast.dump(expr))

    return self.provider.create_query(expr)
