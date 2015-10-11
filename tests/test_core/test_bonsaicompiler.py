import ast
import unittest

from rx.internal.bonsaicompiler import BonsaiCompiler


class TestBonsaiCompiler(unittest.TestCase):

    def test_constant(self):
        const = "42"
        expr = ast.parse(const, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        self.assertEqual(bonsai, [":", 42])

    def test_string(self):
        const = "'42'"
        expr = ast.parse(const, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        self.assertEqual(bonsai, "42")

    def test_unary_negate(self):
        const = "-a"
        expr = ast.parse(const, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        self.assertEqual(bonsai, ["-", [":", "a"]])

    def test_unary_not(self):
        const = "not True"
        expr = ast.parse(const, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        self.assertEqual(bonsai, ["!", [":", True]])

    def test_conditional_expression(self):
        const = "x if b else y"
        expr = ast.parse(const, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        self.assertEqual(bonsai, ["?:", [":", "b"], [":", "x"], [":", "y"]])

    def test_lambda(self):
        identity = "lambda x: x"
        expr = ast.parse(identity, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        self.assertEqual(bonsai, ["=>", ["$", "x"], [["$", "x"]]])

    def test_lambda_x_plus_y(self):
        identity = "lambda x,y: x+y"
        expr = ast.parse(identity, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        self.assertEqual(bonsai, ["=>", ["+", ["$", "x"], ["$", "y"]], [["$", "x"], ["$", "y"]]])

    def test_invocation_expression(self):
        func = "len(x)"
        expr = ast.parse(func, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        #self.assertEqual(bonsai, ["()", "len", ["$", "x"]])

    def test_member_expression(self):
        member = "x.Length"
        expr = ast.parse(member, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        self.assertEqual(bonsai, [".", "Length", [":", "x"]])

    def test_index_expressions(self):
        code = "xs[10]"
        expr = ast.parse(code, mode="eval")
        bonsai = BonsaiCompiler().visit(expr)

        self.assertEqual(bonsai, ["[]", [":", "xs"], [":", 10]])
