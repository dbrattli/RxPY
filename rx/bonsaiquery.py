import json
import ast

import astor

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


class BonsaiCompiler(ast.NodeVisitor):
    def __init__(self):
        self.json = None

        super(BonsaiCompiler, self).__init__()

    def visit_Attribute(self, node):
        #print("visit_Attribute")
        #print(node.attr)
        return [self.visit(node.value), node.attr]

    def visit_BinOp(self, node):
        ops = {
            ast.Mult: "*",
            ast.Add: "+",
            ast.And: "&",
            ast.Sub: "-",
            ast.Div: "/",
            ast.Mod: "%",
            ast.LShift: "<<",
            ast.RShift: ">>",
            ast.BitAnd: "&",
            ast.BitOr: "|",
            ast.BitXor: "^"
        }

        return [ops[type(node.op)], self.visit(node.left), self.visit(node.right)]

    def visit_UnaryOp(self, node):
        ops = {
            ast.Invert: "~",
            ast.Not: "!",
            ast.UAdd: "+",
            ast.USub: "-"
        }

        op = ops[type(node.op)]
        return [op, self.visit(node.operand)]

    def visit_Call(self, node):
        attr= self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]

        method = attr[1]
        source = attr[0]

        return [".()", method, source, args]

    def visit_arg(self, node):
        return ["$", node.arg]

    def visit_Str(self, node):
        return "%s" % node.s

    def visit_Compare(self, node):
        #print("visit_Compare")
        #print(node.left)
        #print(node.ops)
        #print(node.comparators)
        ops = {
            ast.Eq: "=",
            ast.NotEq: "!=",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">=",
            #ast.Is: ""
            #ast.IsNot: "",
            #ast.In "",
            #ast.NotIn: ""
        }
        op = ops[type(node.ops[0])]
        return [ op, self.visit(node.left), self.visit(node.comparators[0]) ]

    def visit_Lambda(self, node):
        args = [self.visit(arg) for arg in node.args.args]
        #print(args)
        #print(node.args.args[0].arg)

        return ["=>", self.visit(node.body), args]

    def visit_Num(self, node):
        return [":", node.n]

    def visit_Name(self, node):
        return [":", str(node.id)]

    def generic_visit(self, node):
        print("generic_visit")
        print(node)
