import ast


class BonsaiCompiler(ast.NodeVisitor):
    def __init__(self):
        self.json = None
        self.params = dict()  # Map of bound variables

        super(BonsaiCompiler, self).__init__()

    def visit_arg(self, node):
        return ["$", node.arg]

    def visit_Attribute(self, node):
        print("visit_Attribute")
        print(node.attr)
        return [".", node.attr, self.visit(node.value)]

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

    def visit_Call(self, node):
        attr = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        print("attr: ", attr)
        print("args: ", args)

        print(node.func)
        print(attr)

        if attr is ast.Attribute:
            source = attr[1]
            method = attr[2]
            return [".()", method, source, args]
        else:
            func = attr[1]
            return ["()", func, *args]

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
        return [op, self.visit(node.left), self.visit(node.comparators[0])]

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_IfExp(self, node):
        return ["?:", self.visit(node.test), self.visit(node.body), self.visit(node.orelse)]

    def visit_Index(self, node):
        return self.visit(node.value)

    def visit_Lambda(self, node):
        args = [self.visit(arg) for arg in node.args.args]
        self.params.update({arg[1]: True for arg in args})
        body = self.visit(node.body)

        return ["=>", body, args]

    def visit_NameConstant(self, node):
        return [":", node.value]

    def visit_Num(self, node):
        return [":", node.n]

    def visit_Name(self, node):
        if node.id in self.params:
            return ["$", str(node.id)]

        return [":", str(node.id)]

    def visit_Str(self, node):
        return "%s" % node.s

    def visit_Subscript(self, node):
        print(node.value)
        print(node.slice)
        return ["[]", self.visit(node.value), self.visit(node.slice)]

    def visit_UnaryOp(self, node):
        ops = {
            ast.Invert: "~",
            ast.Not: "!",
            ast.UAdd: "+",
            ast.USub: "-"
        }

        op = ops[type(node.op)]
        return [op, self.visit(node.operand)]

    def generic_visit(self, node):
        print("generic_visit")
        print(node)
