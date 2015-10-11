import json
import ast

import astor

from rx.internal.bonsaicompiler import BonsaiCompiler

from .abstractobserver import AbstractObserver
from .observer import Observer
from .qbservable import Qbservable


class BonsaiQueryProvider(object):
    def create_query(self, expression):
        if not expression:
            raise NotImplementedError

        return BonsaiQuery(expression=expression)

    def __repr__(self):
        return astor.to_source(self.expression)

    def __str__(self):
        return self.__repr__()


class BonsaiQuery(Qbservable):
    def __init__(self, source=None, expression=None):
        self.source = source
        self.expression = expression or ast.Name(self, ast.Load())

        provider = BonsaiQueryProvider()

        super(BonsaiQuery, self).__init__(self._subscribe, provider, self.expression)

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
            print(astor.dump(self.expression))
            bonsai = BonsaiCompiler()
            output = bonsai.visit(self.expression)
            print(json.dumps(output, indent="   "))

        #return self.source.subscribe(observer)

    def __repr__(self):
        return str(self)

    def __str__(self):
        expr = self.expression
        if expr and getattr(expr, "id", None) == self:
            if self.source:
                return str(self.source)

            return "BonsaiQuery"

        return astor.to_source(self.expression)
