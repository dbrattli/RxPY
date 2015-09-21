import ast
from . import astdump

from .abstractobserver import AbstractObserver
from .observer import Observer
from .qbservable import Qbservable


class ObservableQueryProvider(object):
    def create_query(self, expression):
        if not expression:
            raise NotImplementedError

        return ObservableQuery(expression=expression)

    def __repr__(self):
        astdump.dumpattrs(self.expression)
        return ast.dump(self.expression)

    def __str__(self):
        print("qbservableQueryProvider:__str__")
        return self.__repr__()


class ObservableQuery(Qbservable):
    def __init__(self, source=None, expression=None):
        self.source = source
        self.expression = expression or ast.Name(self, ast.Load())

        provider = ObservableQueryProvider()

        super(ObservableQuery, self).__init__(self._subscribe, provider, self.expression)

    def _subscribe(self, on_next=None, on_error=None, on_completed=None,
                   observer=None):
        """Subscribe an observer to the observable sequence.

        Returns the source sequence whose subscriptions and unsubscriptions
        happen on the specified scheduler.

        1 - source.subscribe()
        2 - source.subscribe(observer)
        3 - source.subscribe(on_next)
        4 - source.subscribe(on_next, on_error)
        5 - source.subscribe(on_next, on_error, on_completed)

        Keyword arguments:
        on_next -- [Optional] Action to invoke for each element in the
            observable sequence.
        on_error -- [Optional] Action to invoke upon exceptional termination of
            the observable sequence.
        on_completed -- [Optional] Action to invoke upon graceful termination
            of the observable sequence.
        observer -- [Optional] The object that is to receive notifications. You
            may subscribe using an observer or callbacks, not both.

        Returns {Diposable} the source sequence whose subscriptions and
        unsubscriptions happen on the specified scheduler.
        """
        # Be forgiving and accept an un-named observer as first parameter
        if isinstance(on_next, AbstractObserver):
            observer = on_next
        elif not observer:
            observer = Observer(on_next, on_error, on_completed)

        if not self.source:
            rewriter = ObservableRewriter()
            body = self.expression #rewriter.visit(self.expression)

            print("------------")
            print(ast.dump(body))
            print("------------")
            # f = ast.Lambda("", body)

            ast.fix_missing_locations(body)
            self.source = eval(compile(body, filename="<ast>", mode="eval"))

        return self.source.subscribe(observer)

    def __str__(self):
        print("ObservableQuery:__str__")

        c = self.expression
        if c and getattr(c, "id", None) == self:
            if self.source:
                print(ast.dump(self.expression))
                return str(self.source)

            return "null"

        def printcb(node, stack):
            nodename = node.__class__.__name__
            print(' '*len(stack)*2 + nodename)

        td = astdump.TreeDumper()
        td.dump(self.expression, callback=printcb)

        return ast.dump(self.expression)


class ObservableRewriter(ast.NodeTransformer):

    def visit_Name(self, node):
        print("visit_Name")
        self.generic_visit(node)

    def visit_Module(self, node):
        print("visit_Module")
        self.generic_visit(node)

    def visit_method_call(self, node):
        pass
